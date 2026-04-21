from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.accounts.models import LanguageLearner


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=50)
    is_onboarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    user_languages: QuerySet['LanguageLearner']

    @classmethod
    def create_user(
        cls,
        email: str,
        username: str,
        password: str,
        **extra_fields
    ) -> "CustomUser":
        return cls.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

    def update_credentials(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        if email:
            self.email = email
        if username:
            self.username = username
        if password:
            self.set_password(password)
        self.save()

    def get_active_language(self) -> Optional['LanguageLearner']:
        return self.user_languages.filter(is_active=True).first()

    def get_all_languages(self) -> QuerySet['LanguageLearner']:
        return self.user_languages.all()

    @property
    def has_completed_onboarding(self) -> bool:
        return self.is_onboarded

    def __str__(self) -> str:
        return self.email