from typing import Optional

from django.db import models
from django.utils import timezone

from apps.study.constants import CARD_XP_CAP


class CardXPRecord(models.Model):
    """
    Entity inside CardProgress aggregate.
    Tracks XP earned per card to enforce per-card XP caps.
    Prevents grinding — a user can't earn infinite XP from one easy card.
    """

    progress = models.OneToOneField(
        'CardProgress',
        on_delete=models.CASCADE,
        related_name='xp_record',
    )
    total_xp_earned = models.IntegerField(default=0)
    last_studied_at = models.DateTimeField(null=True, blank=True)

    # ── Convenience accessors ─────────────────────────────────────────────────

    @property
    def learner(self):
        """
        LanguageLearner — accessed through CardProgress.
        Named `user` on the FK but exposed as `learner` for clarity.
        """
        return self.progress.user

    @property
    def card(self):
        return self.progress.flashcard

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def get_or_create_record(cls, progress: 'CardProgress') -> 'CardXPRecord':
        record, _ = cls.objects.get_or_create(progress=progress)
        return record

    # ── Queries ──────────────────────────────────────────────────────────────

    def remaining_xp_capacity(self) -> int:
        """How much XP this card can still award. Cap is a domain constant."""
        return max(0, CARD_XP_CAP - self.total_xp_earned)

    def is_capped(self) -> bool:
        return self.total_xp_earned >= CARD_XP_CAP

    def is_cap_expired(self, reset_after_days: int = 30) -> Optional[bool]:
        """
        True if enough time has passed to reset the cap.
        Allows old vocabulary to reward XP again after a long break.
        Returns None if card has never been studied.
        """
        if not self.last_studied_at:
            return None
        return (timezone.now() - self.last_studied_at).days >= reset_after_days

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def add_xp(self, amount: int) -> int:
        """
        Adds XP respecting the per-card cap.
        Returns actual XP awarded (may be less than amount if near cap).
        Does NOT save — caller responsible.
        """
        allowed = self.remaining_xp_capacity()
        awarded = min(amount, allowed)
        self.total_xp_earned += awarded
        self.last_studied_at  = timezone.now()
        return awarded

    def reset_cap(self) -> None:
        """
        Resets the card's XP cap after a long break.
        Does NOT save — caller responsible.
        """
        self.total_xp_earned = 0
        self.last_studied_at = None