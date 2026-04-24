from apps.decks.forms import UpdateFlashcardForm
from apps.decks.repositories import DeckRepository
from apps.decks.results import UpdateFlashcardResult, FlashcardDto


class UpdateFlashcardUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, flashcard_id: int, form: UpdateFlashcardForm) -> UpdateFlashcardResult:
        flashcard = self.deck_repo.get_flashcard_by_id(flashcard_id)
        if flashcard is None:
            return UpdateFlashcardResult(success=False, error='Flashcard not found.')
        if not flashcard.deck.is_owned_by(user):
            return UpdateFlashcardResult(success=False, error='Not your flashcard.')

        flashcard.update(**{
            k: v for k, v in form.cleaned_data.items() if v
        })
        flashcard = self.deck_repo.save_flashcard(flashcard)
        return UpdateFlashcardResult(success=True, flashcard=FlashcardDto.from_model(flashcard))