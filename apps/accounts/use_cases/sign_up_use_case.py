from dataclasses import dataclass

from apps.accounts.models import CustomUser
from apps.accounts.repositories import UserRepository
from shared.domain_events import UserRegistered
from shared.event_bus import EventBus


@dataclass
class SignupResult:
    success: bool
    user:    CustomUser | None = None
    error:   str | None        = None


class SignupUseCase:
    """
    Creates a new user from a valid SignupForm.
    Assumes form.is_valid() was already called by the view.

    Why repo.save() instead of form.save()?
    form.save() is a Django shortcut that bypasses our repo layer.
    We call form.save(commit=False) to get the User instance,
    then repo.save() to persist it — keeping all DB writes in repos.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, form) -> SignupResult:
        try:
            # commit=False — gives us the instance without hitting DB
            user = form.save(commit=False)
            # repo is the only thing that saves to DB
            self.user_repo.save(user)

            # publish event — notifications/analytics react without coupling
            EventBus.publish(UserRegistered(
                user_id=user.id,
                email=user.email,
                username=user.username,
            ))

            return SignupResult(success=True, user=user)

        except Exception as e:
            return SignupResult(success=False, error=str(e))