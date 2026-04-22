from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from apps.accounts.models.custom_user import CustomUser
    from apps.languages.models import Language, ProficiencyLevel


class LanguageLearner(models.Model):
    """
    Entity — represents a User's enrollment in a specific Language.

    Bridges the Accounts and Study bounded contexts.
    XP and level live here because progression belongs to the learner,
    not to the study session (sessions are temporary, progress is permanent).

    XP logic, level checking, and event creation live in XPAwardService.
    This model only holds state and exposes simple state toggles.
    """

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='user_languages',
    )
    language = models.ForeignKey(
        'languages.Language',
        on_delete=models.CASCADE,
        related_name='language_learners',
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
        unique_together = ('user', 'language')

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, user: 'CustomUser', language: 'Language') -> 'LanguageLearner':
        return cls.objects.create(
            user=user,
            language=language,
            enrolled_at=timezone.now(),
        )

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def __str__(self) -> str:
        return f"{self.user.username} → {self.language.name}"