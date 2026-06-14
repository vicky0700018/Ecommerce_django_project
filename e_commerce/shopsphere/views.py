from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import CustomUser
import uuid

def home(request):
   return render(request, 'base.html')

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
        # Since username is required by AbstractUser but we want to use email, 
        # we can generate a random username or use part of the email.
        base_username = email.split('@')[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        try:
            user = CustomUser.objects.create(
                username=unique_username,
                full_name=full_name,
                email=email,
                password=make_password(password)
            )
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('register')
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return redirect('register')

    return render(request, 'register.html')

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
            
            if user and user.check_password(password):
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
