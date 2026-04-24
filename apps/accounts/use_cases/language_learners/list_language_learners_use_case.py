from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.results.language_learner_results import ListLanguageLearnersResult, LanguageLearnerDto


class ListLanguageLearnersUseCase:
    def __init__(self, repo: LanguageLearnerRepository):
        self.repo = repo

    def execute(self, user) -> ListLanguageLearnersResult:
        learners = self.repo.get_all_for_user(user)
        return ListLanguageLearnersResult(
            success=True,
            learners=[LanguageLearnerDto.from_model(ll) for ll in learners],
        )