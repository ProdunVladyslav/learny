from django.db.models import QuerySet

from apps.accounts.models import LanguageLearner
from apps.study.models import StudySession
from shared.repositories import BaseRepository


class StudySessionRepository(BaseRepository[StudySession]):
    def __init__(self):
        super().__init__(StudySession)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_with_answers(self, session_id: int) -> StudySession:
        """Fetches session + all card answers in one query."""
        return (
            self._model.objects
            .prefetch_related('card_answers', 'card_answers__flashcard')
            .get(id=session_id)
        )

    def get_active_for_learner(self, learner: LanguageLearner) -> StudySession | None:
        """Returns the currently open session for a learner, if any."""
        return (
            self._model.objects
            .filter(user=learner, ended_at__isnull=True)
            .first()
        )

    def get_history_for_learner(self, learner: LanguageLearner) -> QuerySet[StudySession]:
        """All completed sessions, most recent first."""
        return (
            self._model.objects
            .filter(user=learner, ended_at__isnull=False)
            .select_related('deck')
            .order_by('-started_at')
        )

    # ── Optimized writes ──────────────────────────────────────────────────────

    def close_session(self, session: StudySession) -> StudySession:
        """Only writes ended_at — nothing else changes when closing."""
        return self.save_fields(session, ['ended_at'])