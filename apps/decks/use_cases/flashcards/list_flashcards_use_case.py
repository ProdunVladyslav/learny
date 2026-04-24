from apps.decks.repositories import DeckRepository
from apps.decks.results import ListFlashcardsResult, FlashcardDto


class ListFlashcardsUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, deck_id: int) -> ListFlashcardsResult:
        deck = self.deck_repo.get_by_id(deck_id)
        if deck is None:
            return ListFlashcardsResult(success=False, error='Deck not found.')
        if not deck.is_owned_by(user):
            return ListFlashcardsResult(success=False, error='Not your deck.')

        flashcards = self.deck_repo.list_flashcards(deck_id)
        return ListFlashcardsResult(
            success=True,
            flashcards=[FlashcardDto.from_model(fc) for fc in flashcards],
        )