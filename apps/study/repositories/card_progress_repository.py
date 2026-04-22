from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import LanguageLearner
from apps.decks.models import Flashcard
from apps.study.models import CardProgress, CardXPRecord
from shared.repositories import BaseRepository


class CardProgressRepository(BaseRepository[CardProgress]):
    def __init__(self):
        super().__init__(CardProgress)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_or_create_for(
        self,
        learner:   LanguageLearner,
        flashcard: Flashcard,
    ) -> CardProgress:
        record, _ = self._model.objects.get_or_create(
            user=learner,
            flashcard=flashcard,
        )
        return record

    def get_due_for_learner(self, learner: LanguageLearner) -> QuerySet[CardProgress]:
        """Cards due for review today — core of the spaced repetition queue."""
        return (
            self._model.objects
            .filter(user=learner, next_review__lte=timezone.now().date())
            .select_related('flashcard', 'xp_record')
            .order_by('next_review')
        )

    def get_new_for_learner(self, learner: LanguageLearner) -> QuerySet[CardProgress]:
        """Cards never studied yet."""
        return (
            self._model.objects
            .filter(user=learner, last_seen_at__isnull=True)
            .select_related('flashcard')
        )

    def get_mastered_for_learner(self, learner: LanguageLearner) -> QuerySet[CardProgress]:
        return (
            self._model.objects
            .filter(user=learner, repetitions__gte=5, ease_factor__gte=2.7)
            .select_related('flashcard')
        )

    def get_with_xp_record(self, progress_id: int) -> CardProgress:
        return (
            self._model.objects
            .select_related('xp_record', 'flashcard')
            .get(id=progress_id)
        )

    # ── Optimized writes ──────────────────────────────────────────────────────

    def save_spaced_repetition(self, progress: CardProgress) -> CardProgress:
        """Only updates SM-2 fields — called after every card answer."""
        return self.save_fields(
            progress,
            ['repetitions', 'ease_factor', 'interval_days', 'next_review', 'last_seen_at'],
        )

    def save_with_xp(self, progress: CardProgress) -> CardProgress:
        """
        Saves progress and its xp_record atomically.
        Why atomic? XP record must always match progress state.
        A crash between the two saves would corrupt the learner's XP.
        """
        with transaction.atomic():
            progress.save()
            progress.xp_record.save()
        return progress

    # ── XPRecord (part of CardProgress aggregate) ─────────────────────────────

    def save_xp_record(self, xp_record: CardXPRecord) -> CardXPRecord:
        xp_record.save()
        return xp_record