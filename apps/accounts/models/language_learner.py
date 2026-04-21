from django.db import models

from apps.languages.models import ProficiencyLevel
from config import settings


class LanguageLearner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='language_learners'
    )
    language = models.ForeignKey(
        'languages.Language',
        on_delete=models.CASCADE,
        related_name='language_learners'
    )
    xp = models.IntegerField(default=0)
    current_level = models.ForeignKey(
        'languages.ProficiencyLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    is_active = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'language')

    @classmethod
    def create(cls, user, language) -> 'LanguageLearner':
        return cls.objects.create(user=user, language=language)

    def apply_xp_delta(self, xp_delta: int) -> bool:
        old_level = self.current_level
        self.xp = max(0, min(10_000, self.xp + xp_delta))
        new_level = ProficiencyLevel.get_for_xp(self.xp)
        level_changed = old_level != new_level
        if level_changed:
            self.current_level = new_level
        return level_changed

    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active'])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    # dunder
    def __str__(self):
        return f"{self.user.username} {self.language.name}"