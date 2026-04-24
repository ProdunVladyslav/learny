from apps.accounts.forms.language_learner_forms import CreateLanguageLearnerForm
from apps.accounts.models import LanguageLearner
from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.results.language_learner_results import CreateLanguageLearnerResult, LanguageLearnerDto


class CreateLanguageLearnerUseCase:
    def __init__(self, repo: LanguageLearnerRepository):
        self.repo = repo

    def execute(self, user, form: CreateLanguageLearnerForm) -> CreateLanguageLearnerResult:
        if not form.is_valid():
            return CreateLanguageLearnerResult(success=False, error='Invalid form.')

        language_to = self.repo.get_language_by_code(form.cleaned_data['language_to_code'])
        if language_to is None:
            return CreateLanguageLearnerResult(success=False, error='Target language not found.')

        language_from = None
        if form.cleaned_data.get('language_from_code'):
            language_from = self.repo.get_language_by_code(form.cleaned_data['language_from_code'])

        # idempotent — return existing if already enrolled
        existing = self.repo.get_for_user_and_language(user, language_to.code)
        if existing:
            return CreateLanguageLearnerResult(
                success=True,
                learner=LanguageLearnerDto.from_model(existing),
            )

        ll = LanguageLearner(
            user=user,
            language_to=language_to,
            language_from=language_from,
        )
        ll = self.repo.save(ll)
        return CreateLanguageLearnerResult(success=True, learner=LanguageLearnerDto.from_model(ll))