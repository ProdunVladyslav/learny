from apps.decks.forms import CreateDeckForm
from apps.decks.models import Deck
from apps.decks.repositories import DeckRepository
from apps.decks.results import CreateDeckResult, DeckDto


class CreateDeckUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, form: CreateDeckForm) -> CreateDeckResult:
        if not form.is_valid():
            return CreateDeckResult(success=False, error='Invalid form.')

        language_to = self.deck_repo.get_language_by_code(
            form.cleaned_data['language_to_code']
        )
        if language_to is None:
            return CreateDeckResult(success=False, error='Target language not found.')

        language_from = None
        if form.cleaned_data.get('language_from_code'):
            language_from = self.deck_repo.get_language_by_code(
                form.cleaned_data['language_from_code']
            )

        deck = Deck(
            owner=user,
            language_to=language_to,
            language_from=language_from,
            title=form.cleaned_data['title'],
            description=form.cleaned_data.get('description') or '',
            is_public=form.cleaned_data.get('is_public') or False,
        )
        deck = self.deck_repo.save_deck(deck)
        return CreateDeckResult(success=True, deck=DeckDto.from_model(deck))