from django.shortcuts import render, redirect

from apps.accounts.decorators import jwt_required
from apps.accounts.forms import SignupForm
from apps.accounts.repositories import UserRepository
from apps.accounts.services.token_service import TokenService
from apps.accounts.use_cases import (
    LoginUseCase,
    LogoutUseCase,
    SignupUseCase,
)


# ── Helpers — instantiate dependencies ───────────────────────────────────────
# In a larger project these would be injected via a DI container.
# For now, instantiated inline — easy to swap for mocks in tests.

def _login_use_case()  -> LoginUseCase:  return LoginUseCase(UserRepository())
def _signup_use_case() -> SignupUseCase: return SignupUseCase(UserRepository())
def _logout_use_case() -> LogoutUseCase: return LogoutUseCase()


# ── Views ─────────────────────────────────────────────────────────────────────

@jwt_required
def dashboard(request):
    return render(request, 'core/pages/dashboard.html')


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method != 'POST':
        return render(request, 'core/pages/registration/login.html')

    result = _login_use_case().execute(
        request,
        username=request.POST.get('username'),
        password=request.POST.get('password'),
    )

    if not result.success:
        return render(
            request,
            'core/pages/registration/login.html',
            {'error': result.error},
        )

    access, refresh = TokenService.generate_tokens(result.user)
    response        = redirect('dashboard')
    TokenService.set_auth_cookies(
        response,
        access,
        refresh,
        remember_me=bool(request.POST.get('remember_me')),
    )
    return response


def logout_view(request):
    _logout_use_case().execute(request)
    response = redirect('login')
    TokenService.clear_auth_cookies(response)
    return response


def signup(request):
    form = SignupForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        result = _signup_use_case().execute(form)

        if result.success:
            access, refresh = TokenService.generate_tokens(result.user)
            response        = redirect('dashboard')
            TokenService.set_auth_cookies(response, access, refresh)
            return response

    return render(request, 'core/pages/registration/signup.html', {'form': form})