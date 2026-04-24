from apps.decks.repositories import DeckRepository
from apps.decks.results import DeleteFlashcardResult


class DeleteFlashcardUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, flashcard_id: int) -> DeleteFlashcardResult:
        flashcard = self.deck_repo.get_flashcard_by_id(flashcard_id)
        if flashcard is None:
            return DeleteFlashcardResult(success=False, error='Flashcard not found.')
        if not flashcard.deck.is_owned_by(user):
            return DeleteFlashcardResult(success=False, error='Not your flashcard.')

        self.deck_repo.delete_flashcard(flashcard)
        return DeleteFlashcardResult(success=True)
