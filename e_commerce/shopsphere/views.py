from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CustomUser, OTP, Category, Product
import uuid

def home(request):
   return render(request, 'home.html')

def product(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')

    products = Product.objects.filter(is_available=True)
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
   return render(request, 'gallery.html')

def about_us(request):
   return render(request, 'about_us.html')

def contact(request):
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
    return render(request, 'orders.html')



