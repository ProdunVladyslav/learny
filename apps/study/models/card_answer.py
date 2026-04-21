from django.db import models
from django.utils import timezone

from apps.study.constants import QuestionType, SLOW_RESPONSE_MS, FAST_RESPONSE_MS


class CardAnswer(models.Model):
    session = models.ForeignKey(
        'study.StudySession',
        on_delete=models.CASCADE,
        related_name='card_answers', )
    flashcard = models.ForeignKey(
        'decks.Flashcard',
        on_delete=models.CASCADE,
        related_name='card_answers'
    )
    question_type = models.CharField(
        max_length=50,
        choices=QuestionType.choices, # type: ignore[arg-type]
    )
    is_correct = models.BooleanField(default=False)
    response_ms = models.IntegerField(null=True, blank=True)
    answered_at = models.DateTimeField()

    @classmethod
    def create(cls, session, flashcard, question_type,
               is_correct: bool, response_ms: int) -> 'CardAnswer':
        return cls.objects.create(
            session=session,
            flashcard=flashcard,
            question_type=question_type,
            is_correct=is_correct,
            response_ms=response_ms,
            answered_at=timezone.now())

    @property
    def was_slow(self) -> bool:
        if self.response_ms is None:
            return False
        return self.response_ms > SLOW_RESPONSE_MS

    @property
    def was_fast(self) -> bool:
        if self.response_ms is None:
            return False
        return self.response_ms <= FAST_RESPONSE_MS

    @property
    def response_speed(self) -> str:
        """Human readable speed bucket."""
        if self.response_ms is None:
            return 'unknown'
        if self.response_ms <= FAST_RESPONSE_MS:
            return 'fast'
        if self.response_ms <= SLOW_RESPONSE_MS:
            return 'medium'
        return 'slow'

    def __str__(self):
        return f"{self.flashcard}: {'correct' if self.is_correct else 'wrong'}"