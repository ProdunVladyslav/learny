from django.db.models import QuerySet

from apps.accounts.models import CustomUser
from apps.decks.models import Deck, Flashcard
from shared.repositories import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    def __init__(self):
        super().__init__(Deck)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_owner(self, user: CustomUser) -> QuerySet[Deck]:
        return self._model.objects.filter(owner=user).select_related('language')

    def get_public(self) -> QuerySet[Deck]:
        return self._model.objects.filter(is_public=True).select_related('language', 'owner')

    def get_with_flashcards(self, deck_id: int) -> Deck:
        """Fetches deck and all its cards — use when you need to study or display a full deck."""
        return (
            self._model.objects
            .prefetch_related('flashcards', 'flashcards__tags')
            .get(id=deck_id)
        )

    def get_by_owner_and_language(
        self,
        user: CustomUser,
        language_id: int,
    ) -> QuerySet[Deck]:
        return self._model.objects.filter(owner=user, language_id=language_id)

    # ── Flashcard (part of Deck aggregate — lives in DeckRepository) ──────────

    def save_flashcard(self, flashcard: Flashcard) -> Flashcard:
        """
        Flashcard is part of the Deck aggregate.
        Persisted through DeckRepository, not a FlashcardRepository.
        """
        flashcard.save()
        return flashcard

    def delete_flashcard(self, flashcard: Flashcard) -> None:
        flashcard.delete()

    def get_flashcards_for_deck(self, deck_id: int) -> QuerySet[Flashcard]:
        return Flashcard.objects.filter(deck_id=deck_id).prefetch_related('tags')