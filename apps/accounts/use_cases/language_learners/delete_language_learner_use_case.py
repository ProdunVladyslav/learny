from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.results.language_learner_results import DeleteLanguageLearnerResult


class DeleteLanguageLearnerUseCase:
    def __init__(self, repo: LanguageLearnerRepository):
        self.repo = repo

    def execute(self, user, ll_id: int) -> DeleteLanguageLearnerResult:
        ll = self.repo.get_by_id(ll_id)
        if ll is None:
            return DeleteLanguageLearnerResult(success=False, error='Not found.')
        if ll.user_id != user.id:
            return DeleteLanguageLearnerResult(success=False, error='Not yours.')

        self.repo.delete(ll)
        return DeleteLanguageLearnerResult(success=True)