from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.use_cases.language_learners.list_language_learners_use_case import ListLanguageLearnersUseCase
from apps.decks.forms import ListDecksFilterForm
from apps.decks.repositories import DeckRepository
from apps.decks.use_cases.decks.list_decks_use_case import ListDecksUseCase
from apps.languages.models import Language


@login_required
def dashboard_view(request):
    ll_result = ListLanguageLearnersUseCase(LanguageLearnerRepository()).execute(request.user)
    learners  = ll_result.learners

    decks_result = ListDecksUseCase(DeckRepository()).execute(
        request.user,
        ListDecksFilterForm(data={}),
    )

    return render(request, 'core/dashboard.html', {
        'learners': learners,
        'decks': decks_result.decks if decks_result.success else [],
        'no_learner': len(learners) == 0,
        'all_languages': Language.objects.filter(is_active=True),
    })