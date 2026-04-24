from apps.decks.repositories import DeckRepository
from apps.decks.results import GetDeckResult, DeckDto


class GetDeckUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, deck_id: int) -> GetDeckResult:
        deck = self.deck_repo.get_by_id(deck_id)
        if deck is None:
            return GetDeckResult(success=False, error='Deck not found.')
        if not deck.is_owned_by(user):
            return GetDeckResult(success=False, error='Not your deck.')

        return GetDeckResult(success=True, deck=DeckDto.from_model(deck))