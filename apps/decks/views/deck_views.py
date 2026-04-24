from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.use_cases.language_learners.list_language_learners_use_case import ListLanguageLearnersUseCase
from apps.decks.forms import CreateDeckForm, UpdateDeckForm, ListDecksFilterForm
from apps.decks.repositories import DeckRepository
from apps.decks.use_cases.decks.create_deck_use_case import CreateDeckUseCase
from apps.decks.use_cases.decks.delete_deck_use_case import DeleteDeckUseCase
from apps.decks.use_cases.decks.get_deck_use_case import GetDeckUseCase
from apps.decks.use_cases.decks.list_decks_use_case import ListDecksUseCase
from apps.decks.use_cases.decks.update_deck_use_case import UpdateDeckUseCase
from apps.languages.models import Language


def _repo():
    return DeckRepository()


class DeckListView(LoginRequiredMixin, View):
    def get(self, request):
        form = ListDecksFilterForm(request.GET)
        result = ListDecksUseCase(_repo()).execute(request.user, form)
        ll_result = ListLanguageLearnersUseCase(LanguageLearnerRepository()).execute(request.user)
        return render(request, 'decks/list.html', {
            'decks': result.decks if result.success else [],
            'filter_form': form,
            'create_form': CreateDeckForm(),
            'languages': Language.objects.filter(is_active=True),
            'learners': ll_result.learners,
            'active_lt': request.GET.get('language_to', ''),
            'active_lf': request.GET.get('language_from', ''),
        })

    def post(self, request):
        form = CreateDeckForm(request.POST)
        languages = Language.objects.filter(is_active=True)
        ll_result = ListLanguageLearnersUseCase(LanguageLearnerRepository()).execute(request.user)
        if not form.is_valid():
            filter_form = ListDecksFilterForm(request.GET)
            list_result = ListDecksUseCase(_repo()).execute(request.user, filter_form)
            return render(request, 'decks/list.html', {
                'decks': list_result.decks if list_result.success else [],
                'filter_form': filter_form,
                'create_form': form,
                'languages': languages,
                'learners': ll_result.learners,
                'error': form.errors,
            })

        result = CreateDeckUseCase(_repo()).execute(request.user, form)
        if result.success:
            return redirect('decks:detail', deck_id=result.deck.id)

        filter_form = ListDecksFilterForm(request.GET)
        list_result = ListDecksUseCase(_repo()).execute(request.user, filter_form)
        return render(request, 'decks/list.html', {
            'decks': list_result.decks if list_result.success else [],
            'filter_form': filter_form,
            'create_form': form,
            'languages': languages,
            'learners': ll_result.learners,
            'error': result.error,
        })

class DeckCreateView(LoginRequiredMixin, View):
    """Standalone create page — used if you want a dedicated URL."""
    def get(self, request):
        return render(request, 'decks/list.html', {'create_form': CreateDeckForm()})

    def post(self, request):
        form = CreateDeckForm(request.POST)
        result = CreateDeckUseCase(_repo()).execute(request.user, form)
        if result.success:
            return redirect('decks:detail', deck_id=result.deck.id)
        return render(request, 'decks/list.html', {'create_form': form, 'error': result.error})


from apps.decks.forms import CreateFlashcardForm, BulkCreateFlashcardsForm

class DeckDetailView(LoginRequiredMixin, View):
    def get(self, request, deck_id):
        result = GetDeckUseCase(_repo()).execute(request.user, deck_id)
        if not result.success:
            return redirect('decks:list')
        flashcards = _repo().list_flashcards(deck_id=deck_id)
        return render(request, 'decks/detail.html', {
            'deck': result.deck,
            'flashcards': flashcards,
            'add_form': CreateFlashcardForm(initial={'deck_id': deck_id}),
            'bulk_form': BulkCreateFlashcardsForm(initial={'deck_id': deck_id}),
        })


class DeckUpdateView(LoginRequiredMixin, View):
    def post(self, request, deck_id):
        form = UpdateDeckForm(request.POST)
        result = UpdateDeckUseCase(_repo()).execute(request.user, deck_id, form)
        return redirect('decks:detail', deck_id=deck_id)


class DeckDeleteView(LoginRequiredMixin, View):
    def post(self, request, deck_id):
        DeleteDeckUseCase(_repo()).execute(request.user, deck_id)
        return redirect('decks:list')