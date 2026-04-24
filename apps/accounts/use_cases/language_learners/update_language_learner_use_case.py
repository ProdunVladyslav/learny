from apps.accounts.forms.language_learner_forms import UpdateLanguageLearnerForm
from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.results.language_learner_results import UpdateLanguageLearnerResult, LanguageLearnerDto

class UpdateLanguageLearnerUseCase:
    def __init__(self, repo: LanguageLearnerRepository):
        self.repo = repo

    def execute(self, user, ll_id: int, form: UpdateLanguageLearnerForm) -> UpdateLanguageLearnerResult:
        if not form.is_valid():
            return UpdateLanguageLearnerResult(success=False, error='Invalid form.')

        ll = self.repo.get_by_id(ll_id)
        if ll is None:
            return UpdateLanguageLearnerResult(success=False, error='Not found.')
        if ll.user_id != user.id:
            return UpdateLanguageLearnerResult(success=False, error='Not yours.')

        if form.cleaned_data.get('language_from_code'):
            language_from = self.repo.get_language_by_code(
                form.cleaned_data['language_from_code']
            )
            ll.language_from = language_from

        if form.cleaned_data.get('is_active') is not None:
            ll.is_active = form.cleaned_data['is_active']

        ll = self.repo.save(ll)
        return UpdateLanguageLearnerResult(success=True, learner=LanguageLearnerDto.from_model(ll))