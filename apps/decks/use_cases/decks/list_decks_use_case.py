from apps.decks.forms import ListDecksFilterForm
from apps.decks.repositories import DeckRepository
from apps.decks.results import ListDecksResult, DeckDto


class ListDecksUseCase:
    def __init__(self, deck_repo: DeckRepository):
        self.deck_repo = deck_repo

    def execute(self, user, form: ListDecksFilterForm) -> ListDecksResult:
        if not form.is_valid():
            return ListDecksResult(success=False, error='Invalid filters.')

        decks = self.deck_repo.list_decks(
            owner=user,
            search=form.cleaned_data.get('search'),
            is_public=form.cleaned_data.get('is_public'),
            language_id=form.cleaned_data.get('language'),
            language_from_code=form.cleaned_data.get('language_from'),  # ← changed
            language_to_code=form.cleaned_data.get('language_to'),  # ← changed
            order_by=form.cleaned_data.get('order_by') or '-created_at',
        )
        return ListDecksResult(
            success=True,
            decks=[DeckDto.from_model(d) for d in decks],
        )