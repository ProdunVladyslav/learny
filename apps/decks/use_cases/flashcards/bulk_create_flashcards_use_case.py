from apps.decks.forms import CreateFlashcardForm, BulkCreateFlashcardsForm
from apps.decks.repositories import DeckRepository
from apps.decks.results import BulkCreateFlashcardsResult
from apps.decks.use_cases.flashcards.create_flashcard_use_case import CreateFlashcardUseCase


class BulkCreateFlashcardsUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo
        self.create_flashcard_uc = CreateFlashcardUseCase(deck_repo)

    def execute(self, user, form: BulkCreateFlashcardsForm) -> BulkCreateFlashcardsResult:
        if not form.is_valid():
            return BulkCreateFlashcardsResult(success=False, error='Invalid form.')

        raw_string = form.cleaned_data['raw_string']
        deck_id = form.cleaned_data['deck_id']

        entries = [e.strip() for e in raw_string.split(';') if e.strip()]

        created = []

        for entry in entries:
            # parse hint if present: "front-back(hint)" or "front-back"
            hint = None
            if '(' in entry and entry.endswith(')'):
                entry, hint = entry[:-1].split('(', 1)

            # split on first '-' only — back text might contain dashes
            if '-' not in entry:
                return BulkCreateFlashcardsResult(success=False, error=f'Malformed entry: "{entry}"')

            front, back = entry.split('-', 1)

            card_form = CreateFlashcardForm(data={
                'front': front.strip(),
                'back': back.strip(),
                'deck_id': deck_id,
                **({'hint': hint.strip()} if hint else {}),
            })

            result = self.create_flashcard_uc.execute(user, card_form)

            if not result.success:
                return BulkCreateFlashcardsResult(success=False, error=result.error)

            created.append(result.flashcard)

        return BulkCreateFlashcardsResult(success=True, flashcards=created)