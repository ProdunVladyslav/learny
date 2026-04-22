from typing import Optional, TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet

if TYPE_CHECKING:
    from apps.accounts.models.language_learner import LanguageLearner


class CustomUser(AbstractUser):
    """
    Aggregate Root for the User cluster (User + UserProfile).

    Why Aggregate Root?
    UserProfile has no meaning without a User. They share a lifecycle.
    All access to UserProfile goes through User.profile — never fetched
    directly in use cases without first having the User.
    """

    email        = models.EmailField(unique=True)
    username     = models.CharField(unique=True, max_length=50)
    is_onboarded = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    # Type hint for reverse relation — not a real field
    user_languages: QuerySet['LanguageLearner']

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create_user(
        cls,
        email:    str,
        username: str,
        password: str,
        **extra_fields,
    ) -> 'CustomUser':
        """
        DDD Factory Method — single entry point for User creation.
        Ensures email is always set (Django's create_user doesn't require it).
        """
        return cls.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def update_credentials(
        self,
        email:    Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Mutates credentials. Does NOT save — use case calls .save() after.
        Why? Unit of Work pattern — the use case decides when to commit.
        Keeping save() out of domain methods makes them testable without DB.
        """
        if email:
            self.email = email
        if username:
            self.username = username
        if password:
            self.set_password(password)

    def mark_onboarded(self) -> None:
        """
        Explicit domain method instead of setting is_onboarded = True directly.
        Makes it searchable — grep mark_onboarded shows all callers.
        Does NOT save — caller responsible.
        """
        self.is_onboarded = True

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_active_language(self) -> Optional['LanguageLearner']:
        return self.user_languages.filter(is_active=True).first()

    def get_all_languages(self) -> QuerySet['LanguageLearner']:
        return self.user_languages.all()

    @property
    def has_completed_onboarding(self) -> bool:
        return self.is_onboarded

    def __str__(self) -> str:
        return self.email