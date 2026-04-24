import json
from apps.decks.forms import CreateFlashcardForm, BulkCreateFlashcardsForm
from apps.decks.repositories import DeckRepository
from apps.decks.results import BulkCreateFlashcardsResult
from apps.decks.use_cases.flashcards.create_flashcard_use_case import CreateFlashcardUseCase

class BulkCreateFlashcardsFromJsonUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo
        self.create_flashcard_uc = CreateFlashcardUseCase(deck_repo)

    def execute(self, user, raw_json: str, deck_id: int) -> BulkCreateFlashcardsResult:
        try:
            entries = json.loads(raw_json)
        except json.JSONDecodeError:
            return BulkCreateFlashcardsResult(success=False, error='Invalid JSON.')

        if not isinstance(entries, list):
            return BulkCreateFlashcardsResult(success=False, error='Expected a JSON array.')

        created = []

        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                return BulkCreateFlashcardsResult(success=False, error=f'Entry {i} is not an object.')

            card_form = CreateFlashcardForm(data={
                'front':     entry.get('front'),
                'back':      entry.get('back'),
                'hint':      entry.get('hint'),
                'audio_url': entry.get('audio_url'),
                'image_url': entry.get('image_url'),
                'deck_id':   deck_id,
            })

            result = self.create_flashcard_uc.execute(user, card_form)

            if not result.success:
                return BulkCreateFlashcardsResult(success=False, error=f'Entry {i}: {result.error}')

            created.append(result.flashcard)

        return BulkCreateFlashcardsResult(success=True, flashcards=created)