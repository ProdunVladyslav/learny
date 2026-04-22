from django.db import models
from django.utils import timezone

from apps.study.constants import QuestionType
from shared.value_objects import ResponseTime


class CardAnswer(models.Model):
    """
    Entity inside the StudySession aggregate.
    Immutable after creation — answers are historical records.
    Uses ResponseTime value object for speed classification.
    """

    session = models.ForeignKey(
        'StudySession',
        on_delete=models.CASCADE,
        related_name='card_answers',
    )
    flashcard = models.ForeignKey(
        'decks.Flashcard',
        on_delete=models.CASCADE,
        related_name='card_answers',
    )
    question_type = models.CharField(
        max_length=50,
        choices=QuestionType.choices,  # type: ignore[arg-type]
    )
    is_correct  = models.BooleanField(default=False)
    response_ms = models.IntegerField(null=True, blank=True)
    answered_at = models.DateTimeField()

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        session:       'StudySession',
        flashcard:     'decks.Flashcard',
        question_type: str,
        is_correct:    bool,
        response_ms:   int | None,
    ) -> 'CardAnswer':
        """
        answered_at is always now() — never passed by caller.
        Passing it in was unnecessary flexibility that invited wrong timestamps.
        """
        return cls.objects.create(
            session=session,
            flashcard=flashcard,
            question_type=question_type,
            is_correct=is_correct,
            response_ms=response_ms,
            answered_at=timezone.now(),
        )

    # ── Queries — delegate to ResponseTime VO ────────────────────────────────

    @property
    def _response_time(self) -> ResponseTime | None:
        if self.response_ms is None:
            return None
        return ResponseTime(self.response_ms)

    @property
    def was_slow(self) -> bool:
        rt = self._response_time
        return rt.is_slow if rt else False

    @property
    def was_fast(self) -> bool:
        rt = self._response_time
        return rt.is_fast if rt else False

    @property
    def response_speed(self) -> str:
        rt = self._response_time
        return rt.bucket if rt else 'unknown'

    def __str__(self) -> str:
        status = 'correct' if self.is_correct else 'wrong'
        return f"{self.flashcard}: {status}"