from django.db.models import QuerySet

from apps.accounts.models import CustomUser, LanguageLearner
from shared.repositories import BaseRepository


class LanguageLearnerRepository(BaseRepository[LanguageLearner]):
    def __init__(self):
        super().__init__(LanguageLearner)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, ll_id: int) -> LanguageLearner | None:
        return (
            self._model.objects
            .select_related('language_to', 'language_from', 'current_level')
            .filter(pk=ll_id).first()
        )

    def get_active_for_user(self, user: CustomUser) -> LanguageLearner | None:
        return (
            self._model.objects
            .select_related('language_to', 'language_from', 'current_level')
            .filter(user=user, is_active=True)
            .first()
        )

    def get_all_for_user(self, user: CustomUser) -> QuerySet[LanguageLearner]:
        return (
            self._model.objects
            .select_related('language_to', 'language_from', 'current_level')
            .filter(user=user)
        )

    def get_with_survey(self, learner_id: int) -> LanguageLearner:
        return (
            self._model.objects
            .select_related('onboarding_survey', 'language_to', 'language_from', 'current_level')
            .get(id=learner_id)
        )

    def get_for_user_and_language(
        self,
        user: CustomUser,
        language_to_code: str,
    ) -> LanguageLearner | None:
        return (
            self._model.objects
            .select_related('language_to', 'language_from')
            .filter(user=user, language_to__code=language_to_code)
            .first()
        )

    def get_language_by_code(self, code: str):
        from apps.languages.models import Language
        return Language.objects.filter(code=code).first()

    # ── Writes ────────────────────────────────────────────────────────────────

    def save(self, ll: LanguageLearner) -> LanguageLearner:
        ll.save()
        return ll

    def delete(self, ll: LanguageLearner) -> None:
        ll.delete()

    def save_active_state(self, learner: LanguageLearner) -> LanguageLearner:
        return self.save_fields(learner, ['is_active'])

    def save_xp_and_level(self, learner: LanguageLearner) -> LanguageLearner:
        return self.save_fields(learner, ['xp', 'current_level_id'])