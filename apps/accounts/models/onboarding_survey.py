from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from apps.accounts.models.language_learner import LanguageLearner
    from apps.languages.models import ProficiencyLevel


class LearningGoal(models.TextChoices):
    """
    Why here and not in constants.py?
    Only used by OnboardingSurvey. Co-location means you find and
    change them together. Extract only if used by 3+ models.
    """
    TRAVEL    = 'travel',    'Travel'
    CAREER    = 'career',    'Career'
    EDUCATION = 'education', 'Education'
    FAMILY    = 'family',    'Family'
    CULTURE   = 'culture',   'Culture & media'
    OTHER     = 'other',     'Other'


class OnboardingSurvey(models.Model):
    """
    Entity — captures user intentions at enrollment time.
    Linked to LanguageLearner (not User) because onboarding
    is per-language, not per-account.
    """

    learner = models.OneToOneField(
        'LanguageLearner',
        on_delete=models.CASCADE,
        related_name='onboarding_survey',
    )
    learning_goal = models.CharField(
        max_length=20,
        choices=LearningGoal.choices,  # type: ignore[arg-type]
        blank=True,
    )
    experience_level = models.ForeignKey(
        'languages.ProficiencyLevel',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    hours_per_week = models.PositiveIntegerField(default=0)
    completed_at   = models.DateTimeField(null=True, blank=True)

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, learner: 'LanguageLearner') -> 'OnboardingSurvey':
        return cls.objects.create(learner=learner)

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def complete(
        self,
        goal:             str,
        experience_level: 'ProficiencyLevel',
        hours_per_week:   int,
    ) -> None:
        """
        Marks survey as complete. Does NOT save — caller responsible.
        Guard: completing an already-completed survey raises an error.
        Why? Silently overwriting onboarding data is a domain violation.
        """
        if self.is_completed:
            raise ValueError("Onboarding survey is already completed.")

        self.completed_at     = timezone.now()
        self.learning_goal    = goal
        self.experience_level = experience_level
        self.hours_per_week   = hours_per_week

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def __str__(self) -> str:
        return f'{self.learning_goal} - {self.experience_level}'