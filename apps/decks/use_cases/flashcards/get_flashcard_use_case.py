from apps.decks.repositories import DeckRepository
from apps.decks.results import GetFlashcardResult, FlashcardDto


class GetFlashcardUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, flashcard_id: int) -> GetFlashcardResult:
        flashcard = self.deck_repo.get_flashcard_by_id(flashcard_id)
        if flashcard is None:
            return GetFlashcardResult(success=False, error='Flashcard not found.')
        if not flashcard.deck.is_owned_by(user):
            return GetFlashcardResult(success=False, error='Not your flashcard.')

        return GetFlashcardResult(success=True, flashcard=FlashcardDto.from_model(flashcard))
