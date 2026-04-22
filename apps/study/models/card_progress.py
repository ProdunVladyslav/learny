from django.db import models
from django.utils import timezone


class CardProgress(models.Model):
    """
    Aggregate Root — spaced repetition state for one (learner, flashcard) pair.

    Tracks how well a user knows a card and when they should see it next.
    SM-2 calculation lives in SpacedRepetitionService — this model only
    stores the result and exposes pure reads on its own state.
    """

    user = models.ForeignKey(
        'accounts.LanguageLearner',
        on_delete=models.CASCADE,
        related_name='card_progresses',
    )
    flashcard = models.ForeignKey(
        'decks.Flashcard',
        on_delete=models.CASCADE,
        related_name='card_progresses',
    )
    repetitions   = models.PositiveIntegerField(default=0)
    ease_factor   = models.FloatField(default=2.5)
    interval_days = models.PositiveIntegerField(default=0)
    next_review   = models.DateField(null=True, blank=True)
    last_seen_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'flashcard')

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def apply_spaced(
        self,
        repetitions:   int,
        ease_factor:   float,
        interval_days: int,
        next_review,
    ) -> None:
        """
        Applies SM-2 result to self.
        Calculation lives in SpacedRepetitionService — this just stores it.
        ease_factor floored at 1.3 — SM-2 algorithm minimum, enforced here
        as a domain invariant so corrupt values can never be stored.
        """
        self.repetitions   = repetitions
        self.ease_factor   = max(1.3, ease_factor)
        self.interval_days = interval_days
        self.next_review   = next_review
        self.last_seen_at  = timezone.now()

    def apply_cram(self, ease_factor: float) -> None:
        """Does NOT save — caller responsible."""
        self.ease_factor  = max(1.3, ease_factor)
        self.last_seen_at = timezone.now()

    def reset(self) -> None:
        """Does NOT save — caller responsible."""
        self.repetitions   = 0
        self.ease_factor   = 2.5
        self.interval_days = 0
        self.next_review   = None
        self.last_seen_at  = None

    # ── Queries — pure reads on own state ────────────────────────────────────

    @property
    def is_new(self) -> bool:
        return self.last_seen_at is None

    @property
    def is_due(self) -> bool:
        if self.next_review is None:
            return True
        return self.next_review <= timezone.now().date()

    @property
    def is_mastered(self) -> bool:
        return self.repetitions >= 5 and self.ease_factor >= 2.7

    @property
    def strength(self) -> int:
        """
        0–100 score representing how well the card is known.
        Combines repetition count (60%) and ease factor (40%).
        """
        MAX_REPS   = 10
        MIN_EASE   = 1.3
        MAX_EASE   = 4.0
        rep_score  = min(self.repetitions / MAX_REPS, 1.0) * 60
        ease_score = max(0.0, (self.ease_factor - MIN_EASE) / (MAX_EASE - MIN_EASE)) * 40
        return round(rep_score + ease_score)

    def __str__(self) -> str:
        return f"{self.user} / {self.flashcard.front} / rep:{self.repetitions}"