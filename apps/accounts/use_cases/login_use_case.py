from dataclasses import dataclass

from django.contrib.auth import authenticate

from apps.accounts.models import CustomUser
from apps.accounts.repositories import UserRepository


@dataclass
class LoginResult:
    success: bool
    user:    CustomUser | None = None
    error:   str | None        = None


class LoginUseCase:
    """
    Authenticates a user with username + password.
    Returns LoginResult — never raises, never touches HTTP.

    Why repo here? authenticate() is Django's built-in — it hits the DB
    internally. UserRepository isn't strictly needed for the lookup itself,
    but is injected for consistency and testability if you later need
    to fetch additional user data post-login (e.g. profile, learner state).
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(
        self,
        request,
        username: str,
        password: str,
    ) -> LoginResult:
        user = authenticate(request, username=username, password=password)

        if user is None:
            return LoginResult(success=False, error='Invalid credentials.')

        return LoginResult(success=True, user=user)