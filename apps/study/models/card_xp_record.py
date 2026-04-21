from typing import Optional

from django.db import models
from django.utils import timezone

from apps.study.constants import CARD_XP_CAP


class CardXPRecord(models.Model):
    progress = models.OneToOneField(
        'study.CardProgress',
        on_delete=models.CASCADE,
        related_name='xp_record'
    )
    total_xp_earned = models.IntegerField(default=0)
    last_studied_at = models.DateTimeField(null=True, blank=True)

    # Convenience accessors — no redundant FKs
    @property
    def learner(self):
        return self.progress.learner  # once CardProgress uses LanguageLearner

    @property
    def card(self):
        return self.progress.flashcard

    @classmethod
    def get_or_create_record(cls, progress: 'CardProgress') -> 'CardXPRecord':
        record, _ = cls.objects.get_or_create(progress=progress)
        return record

    # --- Querying ---

    def remaining_xp_capacity(self, cap: int) -> int:
        """How much XP this card can still give."""
        return max(0, cap - self.total_xp_earned)

    def is_capped(self, cap: int) -> bool:
        """Whether this card has reached its XP limit."""
        return self.total_xp_earned >= cap

    def is_cap_expired(self, reset_after_days: int = 30) -> Optional[bool]:
        """
        True if enough time has passed to reset the cap.
        Allows old vocabulary to reward XP again after a long break.
        """
        if not self.last_studied_at:
            return None
        return (timezone.now() - self.last_studied_at).days >= reset_after_days

    # --- Mutations ---

    def add_xp(self, amount: int) -> int:
        """
        Adds XP, respecting the cap. Returns actual XP awarded.
        Does NOT save — caller is responsible for save().
        """
        allowed = self.remaining_xp_capacity(cap=CARD_XP_CAP)
        awarded = min(amount, allowed)
        self.total_xp_earned += awarded
        self.last_studied_at  = timezone.now()
        return awarded

    def reset_cap(self) -> None:
        """
        Resets the card's XP cap (e.g. after 30-day break).
        Does NOT save — caller is responsible for save().
        """
        self.total_xp_earned = 0
        self.last_studied_at = None