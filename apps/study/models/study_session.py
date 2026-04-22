from django.db import models
from django.utils import timezone

from apps.study.constants import StudyMode


class StudySession(models.Model):
    """
    Aggregate Root for a study interaction.
    CardAnswers are owned by this session — access via session.card_answers.
    Created → filled with answers → closed. Immutable after closing.
    """

    user = models.ForeignKey(
        'accounts.LanguageLearner',
        on_delete=models.CASCADE,
        related_name='study_sessions',
    )
    deck = models.ForeignKey(
        'decks.Deck',
        on_delete=models.CASCADE,
        related_name='study_sessions',
    )
    mode = models.CharField(
        max_length=20,
        choices=StudyMode.choices,  # type: ignore[arg-type]
    )
    cards_target = models.PositiveIntegerField(null=True, blank=True)
    started_at   = models.DateTimeField()
    ended_at     = models.DateTimeField(null=True, blank=True)

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user:         'accounts.LanguageLearner',
        deck:         'decks.Deck',
        mode:         str,
        cards_target: int | None,
    ) -> 'StudySession':
        return cls.objects.create(
            user=user,
            deck=deck,
            mode=mode,
            cards_target=cards_target,
            started_at=timezone.now(),
        )

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def close(self) -> None:
        """
        Marks session as finished.
        Guard: closing twice is a domain error — would corrupt duration_seconds.
        Does NOT save — caller responsible.
        """
        if self.is_finished:
            raise ValueError("StudySession is already closed.")
        self.ended_at = timezone.now()

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def is_finished(self) -> bool:
        return self.ended_at is not None

    def has_reached_target(self) -> bool:
        if not self.cards_target:
            return False
        return self.card_answers.count() >= self.cards_target

    @property
    def duration_seconds(self) -> float | None:
        if not self.ended_at:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    def __str__(self) -> str:
        return f'{self.user} | {self.deck} | {self.mode}'