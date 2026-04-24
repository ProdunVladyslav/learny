from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from apps.accounts.models.custom_user import CustomUser
    from apps.languages.models import Language, ProficiencyLevel


class LanguageLearner(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='user_languages',
    )
    language_to = models.ForeignKey(
        'languages.Language',
        on_delete=models.CASCADE,
        related_name='learners_studying',
    )
    language_from = models.ForeignKey(
        'languages.Language',
        on_delete=models.SET_NULL,
        null=True,
        related_name='learners_native',
    )
    xp = models.IntegerField(default=0)
    current_level = models.ForeignKey(
        'languages.ProficiencyLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    is_active   = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # unique_together = ('user', 'language_to')
        pass

    @classmethod
    def create(
        cls,
        user: 'CustomUser',
        language_to: 'Language',
        language_from: 'Language',
    ) -> 'LanguageLearner':
        return cls.objects.create(
            user=user,
            language_to=language_to,
            language_from=language_from,
            enrolled_at=timezone.now(),
        )

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def __str__(self) -> str:
        if self.language_from:
            return f"{self.user.username} {self.language_from.code} → {self.language_to.code}"
        return f"{self.user.username} → {self.language_to.code}"