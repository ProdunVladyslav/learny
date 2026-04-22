from django.db.models import QuerySet

from apps.accounts.models import CustomUser, LanguageLearner
from shared.repositories import BaseRepository


class LanguageLearnerRepository(BaseRepository[LanguageLearner]):
    def __init__(self):
        super().__init__(LanguageLearner)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_active_for_user(self, user: CustomUser) -> LanguageLearner | None:
        return (
            self._model.objects
            .select_related('language', 'current_level')
            .filter(user=user, is_active=True)
            .first()
        )

    def get_all_for_user(self, user: CustomUser) -> QuerySet[LanguageLearner]:
        return (
            self._model.objects
            .select_related('language', 'current_level')
            .filter(user=user)
        )

    def get_with_survey(self, learner_id: int) -> LanguageLearner:
        """Fetches learner + onboarding survey in one query."""
        return (
            self._model.objects
            .select_related('onboarding_survey', 'language', 'current_level')
            .get(id=learner_id)
        )

    def get_by_user_and_language(
        self,
        user: CustomUser,
        language_id: int,
    ) -> LanguageLearner | None:
        return self._model.objects.filter(user=user, language_id=language_id).first()

    # ── Optimized writes ──────────────────────────────────────────────────────

    def save_active_state(self, learner: LanguageLearner) -> LanguageLearner:
        """Only updates is_active column — avoids overwriting XP on concurrent requests."""
        return self.save_fields(learner, ['is_active'])

    def save_xp_and_level(self, learner: LanguageLearner) -> LanguageLearner:
        """Only updates XP and level — used after study session completion."""
        return self.save_fields(learner, ['xp', 'current_level'])