from apps.accounts.repositories import LanguageLearnerRepository


def learners(request):
    if not request.user.is_authenticated:
        return {'learners': []}
    from apps.accounts.use_cases.language_learners.list_language_learners_use_case import ListLanguageLearnersUseCase
    result = ListLanguageLearnersUseCase(LanguageLearnerRepository()).execute(request.user)
    return {'learners': result.learners}