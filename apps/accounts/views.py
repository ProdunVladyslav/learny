from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from apps.accounts.forms.auth_forms import LoginForm, SignupForm
from apps.accounts.forms.language_learner_forms import CreateLanguageLearnerForm
from apps.accounts.repositories import UserRepository, LanguageLearnerRepository
from apps.accounts.services.token_service import TokenService
from apps.accounts.use_cases import (
    LoginUseCase,
    LogoutUseCase,
    SignupUseCase,
)
from apps.accounts.use_cases.language_learners.create_language_learner_use_case import CreateLanguageLearnerUseCase


# ── Helpers — instantiate dependencies ───────────────────────────────────────
# In a larger project these would be injected via a DI container.
# For now, instantiated inline — easy to swap for mocks in tests.

def _login_use_case()  -> LoginUseCase:  return LoginUseCase(UserRepository())
def _signup_use_case() -> SignupUseCase: return SignupUseCase(UserRepository())
def _logout_use_case() -> LogoutUseCase: return LogoutUseCase()


# ── Views ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        result = _login_use_case().execute(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if result.success:
            access, refresh = TokenService.generate_tokens(result.user)
            response = redirect('core:dashboard')
            TokenService.set_auth_cookies(
                response, access, refresh,
                remember_me=form.cleaned_data['remember_me'],
            )
            return response
        form.add_error(None, result.error)

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    _logout_use_case().execute(request)
    response = redirect('accounts:login')
    TokenService.clear_auth_cookies(response)
    return response


def signup(request):
    form = SignupForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        result = _signup_use_case().execute(form)

        if result.success:
            access, refresh = TokenService.generate_tokens(result.user)
            response        = redirect('core:dashboard')
            TokenService.set_auth_cookies(response, access, refresh)
            return response

    return render(request, 'accounts/signup.html', {'form': form})

class LanguageLearnerCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = CreateLanguageLearnerForm(request.POST)
        CreateLanguageLearnerUseCase(LanguageLearnerRepository()).execute(request.user, form)
        next_url = request.POST.get('next') or 'core:dashboard'
        return redirect(next_url)