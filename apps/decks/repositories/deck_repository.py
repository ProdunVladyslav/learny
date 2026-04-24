from django.db.models import QuerySet

from apps.accounts.models import CustomUser
from apps.decks.models import Deck, Flashcard
from shared.repositories import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    def __init__(self):
        super().__init__(Deck)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_owner(self, user: CustomUser) -> QuerySet[Deck]:
        return self._model.objects.filter(owner=user).select_related('language_to', 'language_from')

    def get_public(self) -> QuerySet[Deck]:
        return self._model.objects.filter(is_public=True).select_related('language_to', 'language_from', 'owner')

    def get_with_flashcards(self, deck_id: int) -> Deck:
        """Fetches deck and all its cards — use when you need to study or display a full deck."""
        return (
            self._model.objects
            .prefetch_related('flashcards', 'flashcards__tags')
            .get(id=deck_id)
        )

    # ── Deck ─────────────────────────────────────────────────
    def get_by_id(self, deck_id: int) -> Deck | None:
        return Deck.objects.filter(pk=deck_id).first()

    def save_deck(self, deck: Deck) -> Deck:
        deck.save()
        return deck

    def delete_deck(self, deck: Deck) -> None:
        deck.delete()

    def list_decks(
            self,
            owner,
            search: str | None = None,
            is_public: bool | None = None,
            language_id: int | None = None,
            language_from_code: str | None = None,  # ← changed
            language_to_code: str | None = None,  # ← changed
            order_by: str = '-created_at',
    ) -> list[Deck]:
        qs = Deck.objects.filter(owner=owner)

        if search:
            qs = qs.filter(title__icontains=search)
        if is_public is not None:
            qs = qs.filter(is_public=is_public)
        if language_id is not None:
            qs = qs.filter(language_to_id=language_id)
        if language_to_code:
            qs = qs.filter(language_to__code=language_to_code)
        if language_from_code:
            qs = qs.filter(language_from__code=language_from_code)

        allowed_orderings = {'created_at', '-created_at', 'title', '-title'}
        if order_by not in allowed_orderings:
            order_by = '-created_at'

        return list(qs.order_by(order_by))

    def get_language_by_id(self, language_id: int):
        from apps.languages.models import Language
        return Language.objects.filter(pk=language_id).first()

    def get_language_by_code(self, language_code: str):
        from apps.languages.models import Language
        return Language.objects.filter(code=language_code).first()

    # ── Flashcard ─────────────────────────────────────────────
    def get_flashcard_by_id(self, flashcard_id: int) -> Flashcard | None:
        return Flashcard.objects.select_related('deck').filter(pk=flashcard_id).first()

    def save_flashcard(self, flashcard: Flashcard) -> Flashcard:
        flashcard.save()
        return flashcard

    def delete_flashcard(self, flashcard: Flashcard) -> None:
        flashcard.delete()

    def list_flashcards(self, deck_id: int) -> list[Flashcard]:
        return list(Flashcard.objects.filter(deck_id=deck_id).order_by('id'))

