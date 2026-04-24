from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from apps.decks.forms import CreateFlashcardForm, BulkCreateFlashcardsForm, UpdateFlashcardForm
from apps.decks.repositories import DeckRepository
from apps.decks.use_cases.flashcards.create_flashcard_use_case import CreateFlashcardUseCase
from apps.decks.use_cases.flashcards.bulk_create_flashcards_use_case import BulkCreateFlashcardsUseCase
from apps.decks.use_cases.flashcards.update_flashcard_use_case import UpdateFlashcardUseCase
from apps.decks.use_cases.flashcards.delete_flashcard_use_case import DeleteFlashcardUseCase


def _repo():
    return DeckRepository()

class FlashcardCreateView(LoginRequiredMixin, View):
    def post(self, request, deck_id):
        form = CreateFlashcardForm(request.POST)
        if form.is_valid():
            CreateFlashcardUseCase(_repo()).execute(request.user, form)
        return redirect('decks:detail', deck_id=deck_id)


class FlashcardBulkCreateView(LoginRequiredMixin, View):
    def post(self, request, deck_id):
        form = BulkCreateFlashcardsForm(request.POST)
        if form.is_valid():
            BulkCreateFlashcardsUseCase(_repo()).execute(request.user, form)
        return redirect('decks:detail', deck_id=deck_id)


class FlashcardUpdateView(LoginRequiredMixin, View):
    def post(self, request, card_id):
        form = UpdateFlashcardForm(request.POST)
        deck_id = request.POST.get('deck_id')
        if form.is_valid():
            UpdateFlashcardUseCase(_repo()).execute(request.user, card_id, form)
        return redirect('decks:detail', deck_id=deck_id)


class FlashcardDeleteView(LoginRequiredMixin, View):
    def post(self, request, card_id):
        deck_id = request.POST.get('deck_id')
        DeleteFlashcardUseCase(_repo()).execute(request.user, card_id)
        return redirect('decks:detail', deck_id=deck_id)