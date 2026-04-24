from dataclasses import dataclass

from apps.accounts.models import CustomUser


@dataclass
class LoginResult:
    success: bool
    user:    CustomUser | None = None
    error:   str | None        = None

@dataclass
class SignupResult:
    success: bool
    user: CustomUser | None = None
    error: str | None = None
