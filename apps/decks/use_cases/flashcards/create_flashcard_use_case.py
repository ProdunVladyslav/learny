from apps.decks.forms import CreateFlashcardForm
from apps.decks.models import Flashcard
from apps.decks.repositories import DeckRepository
from apps.decks.results import CreateFlashcardResult, FlashcardDto
from shared.domain_events import FlashcardAddedToDeck
from shared.event_bus import EventBus


class CreateFlashcardUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, form: CreateFlashcardForm) -> CreateFlashcardResult:
        if not form.is_valid():
            return CreateFlashcardResult(success=False, error=form.errors.__str__())

        deck = self.deck_repo.get_by_id(form.cleaned_data['deck_id'])
        if deck is None:
            return CreateFlashcardResult(success=False, error='Deck not found.')
        if deck.owner != user:
            return CreateFlashcardResult(success=False, error='Not your deck.')

        flashcard = Flashcard.create(
            deck=deck,
            front=form.cleaned_data['front'],
            back=form.cleaned_data['back'],
        )

        flashcard = self.deck_repo.save_flashcard(flashcard)

        # ── Publish domain event ──────────────────────────────────────────────
        # Fired after save so flashcard_id is guaranteed to exist.
        # Listeners (e.g. CardProgressInitializationService) react asynchronously
        # and are responsible for their own DB writes.
        EventBus.publish(FlashcardAddedToDeck(
            flashcard_id=flashcard.id,
            deck_id=deck.id,
            language_to_id=deck.language_to_id,
            language_from_id=deck.language_from_id,  # None when not set
        ))

        return CreateFlashcardResult(
            success=True,
            flashcard=FlashcardDto.from_model(flashcard),
        )