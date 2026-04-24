from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.results.language_learner_results import GetLanguageLearnerResult, LanguageLearnerDto


class GetLanguageLearnerUseCase:
    def __init__(self, repo: LanguageLearnerRepository):
        self.repo = repo

    def execute(self, user, ll_id: int) -> GetLanguageLearnerResult:
        ll = self.repo.get_by_id(ll_id)
        if ll is None:
            return GetLanguageLearnerResult(success=False, error='Not found.')
        if ll.user_id != user.id:
            return GetLanguageLearnerResult(success=False, error='Not yours.')
        return GetLanguageLearnerResult(success=True, learner=LanguageLearnerDto.from_model(ll))