from django import forms
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.decorators import jwt_required
from config import settings

User = get_user_model()

@jwt_required
def dashboard(request):
    return render(request, 'core/pages/dashboard.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            response = redirect('dashboard')

            # Store tokens in HttpOnly cookies (not localStorage!)
            response.set_cookie(
                'access_token',
                access,
                max_age=60 * 15,  # 15 min
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                max_age=60 * 60 * 24 * 14 if remember_me else None,  # 14 days or session
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )
            return response
        else:
            return render(request, 'core/pages/registration/login.html',
                          {'error': 'Invalid credentials.'})

    return render(request, 'core/pages/registration/login.html')

class SignupForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model  = User
        fields = ['email', 'username', 'password1', 'password2']

def logout_view(request):
    logout(request)
    response = redirect('login')
    response.set_cookie('access_token', '', max_age=0, path='/', httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', '', max_age=0, path='/', httponly=True, samesite='Lax')
    return response

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            response = redirect('dashboard')
            response.set_cookie(
                'access_token', access,
                max_age=60 * 15,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )
            response.set_cookie(
                'refresh_token', str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )
            return response
    else:
        form = SignupForm()
    return render(request, 'core/pages/registration/signup.html', {'form': form})

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')
