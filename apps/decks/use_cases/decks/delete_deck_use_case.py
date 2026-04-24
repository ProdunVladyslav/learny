from apps.decks.repositories import DeckRepository
from apps.decks.results import DeleteDeckResult


class DeleteDeckUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, deck_id: int) -> DeleteDeckResult:
        deck = self.deck_repo.get_by_id(deck_id)
        if deck is None:
            return DeleteDeckResult(success=False, error='Deck not found.')
        if not deck.is_owned_by(user):
            return DeleteDeckResult(success=False, error='Not your deck.')

        self.deck_repo.delete_deck(deck)
        return DeleteDeckResult(success=True)