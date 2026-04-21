from django.db import models
from django.utils import timezone

from apps.accounts.models import LanguageLearner

class LearningGoal(models.TextChoices):
    TRAVEL = 'travel', 'Travel'
    CAREER = 'career', 'Career'
    EDUCATION = 'education', 'Education'
    FAMILY = 'family', 'Family'
    CULTURE = 'culture', 'Culture & media'
    OTHER = 'other', 'Other'

class OnboardingSurvey(models.Model):

    learner = models.OneToOneField(
        LanguageLearner,
        on_delete=models.CASCADE,
        related_name='onboarding_survey',
    )
    learning_goal = models.CharField(
        max_length=20,
        choices=LearningGoal.choices, # type: ignore[arg-type]
        blank=True,
    )
    experience_level = models.ForeignKey(
        'languages.ProficiencyLevel',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    hours_per_week = models.PositiveIntegerField()
    completed_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create(cls, learner: 'LanguageLearner') -> 'OnboardingSurvey':
        return cls.objects.create(
            learner=learner
        )

    def complete(self, goal, experience_level, hours_per_week) -> None:
        self.completed_at = timezone.now()
        self.learning_goal = goal
        self.experience_level = experience_level
        self.hours_per_week = hours_per_week

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def __str__(self):
        return f'{self.learning_goal} - {self.experience_level}'