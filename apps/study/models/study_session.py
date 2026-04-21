from django.db import models
from django.utils import timezone

from apps.study.constants import StudyMode


class StudySession(models.Model):
    user = models.ForeignKey(
        'accounts.LanguageLearner',
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    deck = models.ForeignKey(
        'decks.Deck',
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    mode = models.CharField(
        max_length=20,
        choices=StudyMode.choices, # type: ignore[arg-type]
    )
    cards_target = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    card_answers: 'QuerySet[CardAnswer]'

    @classmethod
    def create(cls, user, deck, mode, cards_target):
        return cls.objects.create(
            user=user,
            deck=deck,
            mode=mode,
            cards_target=cards_target,
            started_at=timezone.now(),
        )

    # Does NOT save — caller is responsible
    def close(self) -> None:
        self.ended_at = timezone.now()

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

    def __str__(self):
        return f'{self.user} {self.deck} {self.mode} {self.cards_target}'

