from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from .models import CustomUser
import random
from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings
# Create your views here.


def send_otp(request):
    """Generate OTP and send to email"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    # Check if email already exists
    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({'error': 'This email is already registered'}, status=400)
    
    try:
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Send email
        send_mail(
            subject="Your OTP Code for Registration",
            message=f"Your verification code is: {otp}\n\nThis code will expire in 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Store OTP in session with email
        request.session['otp'] = otp
        request.session['otp_email'] = email
        request.session['otp_created_at'] = timezone.now().isoformat()
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'OTP sent to {email}'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to send OTP: {str(e)}'
        }, status=500)


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            if not user.is_active:
                messages.error(request, "Verify your email first (OTP)")
                return redirect('account_login')
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)

    context = {'form1': userForm, 'form2': voterForm}

    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            
            email = userForm.cleaned_data['email']
            entered_otp = userForm.cleaned_data['otp']
            session_otp = request.session.get('otp')
            session_email = request.session.get('otp_email')
            session_otp_created = request.session.get('otp_created_at')
            
            # Validate OTP was requested
            if not session_otp or not session_email:
                messages.error(request, "Please click 'Send OTP' button first")
                return render(request, "voting/reg.html", context)
            
            # Validate email matches
            if email != session_email:
                messages.error(request, "Email does not match OTP email")
                return render(request, "voting/reg.html", context)
            
            # Check OTP expiry (5 minutes)
            if session_otp_created:
                otp_time = datetime.fromisoformat(session_otp_created)
                if timezone.now() > otp_time + timedelta(minutes=5):
                    messages.error(request, "OTP expired. Please request a new one")
                    request.session.pop('otp', None)
                    request.session.pop('otp_email', None)
                    request.session.pop('otp_created_at', None)
                    return render(request, "voting/reg.html", context)
            
            # Validate OTP
            if entered_otp != session_otp:
                messages.error(request, "Invalid OTP. Please try again")
                return render(request, "voting/reg.html", context)
            
            # OTP is valid, proceed with registration
            user = userForm.save(commit=False)
            user.is_active = True  # Auto-activate since OTP was verified
            user.set_password(userForm.cleaned_data['password'])
            
            voter = voterForm.save(commit=False)
            voter.admin = user
            voter.verified = True
            
            user.save()
            voter.save()
            
            # Clear OTP from session
            request.session.pop('otp', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_created_at', None)
            
            messages.success(request, "Registration successful! You can now login")
            return redirect('account_login')

        else:
            messages.error(request, "Form validation failed")

    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))
