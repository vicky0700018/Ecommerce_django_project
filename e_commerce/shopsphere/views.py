from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CustomUser, OTP, Category, Product, TeamMember, Gallery, ContactMessage, Order
from decimal import Decimal
import uuid
import razorpay
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
client = razorpay.Client(
    auth=(
        settings.RAZORPAY_API_KEY,
        settings.RAZORPAY_API_SECRET
    )
)

def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).select_related('category')
    featured_products = products[:8]
    new_arrivals = products.order_by('-created_at')[:8]
    best_sellers = products.order_by('-id')[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
    }
    return render(request, 'home.html', context)

def product(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')

    products = Product.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'product.html', context)

def category(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'category.html', context)

def gallery(request):
    images = Gallery.objects.all()
    return render(request, 'gallery.html', {'images': images})

def about_us(request):
    team_members = TeamMember.objects.all()
    return render(request, 'about_us.html', {'team_members': team_members})

def contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        agree = request.POST.get('agree')

        if not first_name or not last_name or not email or not subject or not message or not agree:
            messages.error(request, 'Please fill in all required fields and agree to the terms and conditions.')
            return redirect('contact')

        try:
            contact_msg = ContactMessage(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            contact_msg.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        except Exception as e:
            messages.error(request, f'Something went wrong while sending your message: {str(e)}')
            
        return redirect('contact')

    return render(request, 'contact.html')

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validations
        if not full_name or not email or not password:
            messages.error(request, 'All fields are required!')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('register')

        # Create user
        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        try:
            user = CustomUser.objects.create(
                username=unique_username,
                full_name=full_name,
                email=email,
                password=make_password(password),
                is_email_verified=False
            )
            user.save()
            
            # Generate and send OTP
            otp = OTP.generate_otp(user)
            send_otp_email(user, otp.code)
            
            messages.success(request, 'Registration successful! Check your email for OTP verification.')
            request.session['email_for_verification'] = email
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return redirect('register')

    return render(request, 'register.html')


def send_otp_email(user, otp_code):
    """Send OTP email to user"""
    subject = 'Email Verification OTP - ShopSphere'
    html_message = render_to_string('otp_email.html', {
        'full_name': user.full_name,
        'otp_code': otp_code
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    """Send welcome email to user after verification"""
    subject = 'Welcome to ShopSphere!'
    html_message = render_to_string('welcome_email.html', {
        'full_name': user.full_name
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def verify_otp(request):
    """Verify OTP and mark email as verified"""
    email = request.session.get('email_for_verification')
    
    if not email:
        messages.error(request, 'Invalid verification request.')
        return redirect('register')
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    
    if user.is_email_verified:
        messages.info(request, 'Email already verified. You can log in now.')
        return redirect('login')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'verify_otp.html', {'email': email})
        
        try:
            otp = OTP.objects.get(user=user)
            
            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return render(request, 'verify_otp.html', {'email': email})
            
            if otp.verify(otp_code):
                # Mark user as email verified
                user.is_email_verified = True
                user.save()
                
                # Send welcome email
                send_welcome_email(user)
                
                # Clear session
                del request.session['email_for_verification']
                
                messages.success(request, 'Email verified successfully! Welcome to ShopSphere. You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'verify_otp.html', {'email': email})
        
        except OTP.DoesNotExist:
            messages.error(request, 'OTP not found. Please register again.')
            return redirect('register')
    
    return render(request, 'verify_otp.html', {'email': email})


def resend_otp(request):
    """Resend OTP to user email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email.')
            return redirect('verify_otp')
        
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            otp = OTP.generate_otp(user)
            send_otp_email(user, otp.code)
            messages.success(request, 'OTP resent successfully. Check your email.')
            request.session['email_for_verification'] = email
            return redirect('verify_otp')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email not found or already verified.')
            return redirect('register')
    
    return redirect('verify_otp')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Validation
        if not email or not password:
            messages.error(request, 'Email and password are required!')
            return redirect('login')

        try:
            # Find user by email
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                messages.error(request, 'Invalid email or password!')
                return redirect('login')
            
            if not user.is_email_verified:
                messages.warning(request, 'Please verify your email first before logging in.')
                request.session['email_for_verification'] = email
                return redirect('verify_otp')
            
            if user.check_password(password):
                # Set backend attribute for proper authentication
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                # Authenticate and login
                auth_login(request, user)
                
                # Handle remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser session
                
                messages.success(request, f'Welcome back, {user.full_name}!')
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password!')
                return redirect('login')
        
        except Exception as e:
            messages.error(request, f'An error occurred during login: {str(e)}')
            return redirect('login')

    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

def wishlist(request):
    """Display wishlist page"""
    return render(request, 'wishlist.html')

def cart(request):
    """Display shopping cart page"""
    return render(request, 'cart.html')
def checkout(request):
    """Display checkout page"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to proceed to checkout.')
        return redirect('/login/?next=/checkout/')

    context = {
        'RAZORPAY_API_KEY': settings.RAZORPAY_API_KEY,
    }

    return render(request, 'checkout.html', context)


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            amount = int(request.POST.get("amount"))

            order = client.order.create({
                "amount": amount,
                "currency": "INR"
            })

            return JsonResponse(order)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            })

    return JsonResponse({
        "success": False,
        "error": "Invalid Request"
    })


def privacy_policy(request):
    """Display privacy policy page"""
    return render(request, 'privacy_policy.html')

def refund_policy(request):
    """Display refund policy page"""
    return render(request, 'refund_policy.html')

def shipping_policy(request):
    """Display shipping policy page"""
    return render(request, 'shipping_policy.html')

def terms_conditions(request):
    """Display terms & conditions page"""
    return render(request, 'terms_conditions.html')

def our_mission(request):
    """Display our mission page"""
    return render(request, 'our_mission.html')

def our_vision(request):
    """Display our vision page"""
    return render(request, 'our_vision.html')

def profile(request):
    """Display user profile page and handle profile updates"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to access your profile.')
        return redirect('login')
        
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name', '').strip()
        user.mobile_no = request.POST.get('mobile_no', '').strip()
        user.alternate_mobile_no = request.POST.get('alternate_mobile_no', '').strip()
        user.gender = request.POST.get('gender', '').strip()
        user.address = request.POST.get('address', '').strip()
        user.city = request.POST.get('city', '').strip()
        user.pincode = request.POST.get('pincode', '').strip()
        
        dob_val = request.POST.get('dob')
        if dob_val:
            user.dob = dob_val
            
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            user.profile_image = profile_image
            
        user.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
        
    return render(request, 'profile.html')

def orders(request):
    """Display user order history page"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to access your orders.')
        return redirect('login')
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


def forgot_password(request):
    """Handle password reset request by sending an OTP to user email"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your registered email address.')
            return redirect('forgot_password')
            
        try:
            user = CustomUser.objects.get(email=email)
            # Generate and send OTP
            otp = OTP.generate_otp(user)
            send_reset_password_email(user, otp.code)
            
            request.session['reset_password_email'] = email
            messages.success(request, 'An OTP has been sent to your email. Please verify to reset your password.')
            return redirect('reset_password')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('forgot_password')
            
    return render(request, 'forgot_password.html')


def send_reset_password_email(user, otp_code):
    """Send password reset OTP email to user"""
    subject = 'Reset Password OTP - ShopSphere'
    html_message = render_to_string('reset_password_email.html', {
        'full_name': user.full_name,
        'otp_code': otp_code
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def reset_password(request):
    """Verify OTP and update user password"""
    if request.user.is_authenticated:
        return redirect('home')
        
    email = request.session.get('reset_password_email')
    if not email:
        messages.error(request, 'Invalid request session. Please request OTP again.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not otp_code or not new_password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'reset_password.html', {'email': email})
            
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html', {'email': email})
            
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'reset_password.html', {'email': email})
            
        try:
            user = CustomUser.objects.get(email=email)
            otp = OTP.objects.get(user=user)
            
            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('forgot_password')
                
            if otp.verify(otp_code):
                # Update password
                user.password = make_password(new_password)
                user.save()
                
                # Delete OTP
                otp.delete()
                
                # Clear session
                del request.session['reset_password_email']
                
                messages.success(request, 'Password reset successful! You can now log in with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'reset_password.html', {'email': email})
                
        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, 'Invalid request or expired OTP.')
            return redirect('forgot_password')
            
    return render(request, 'reset_password.html', {'email': email})

@csrf_exempt
def save_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            order = Order.objects.create(
                user=request.user,
                order_id=data["order_id"],
                payment_id=data.get("payment_id"),
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                address=data["address"],
                city=data["city"],
                pincode=data["pincode"],
                amount=Decimal(str(data["amount"])),
                payment_method=data["payment_method"],
                status="Paid" if data["payment_method"] == "ONLINE" else "Pending",
                product=data.get("product", "Order Items"),
            )

            return JsonResponse({
                "success": True,
                "order": order.order_id
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)

    return JsonResponse({"success": False}, status=405)

