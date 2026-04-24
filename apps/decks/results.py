from __future__ import annotations
from dataclasses import dataclass, field


# ── DTOs ─────────────────────────────────────────────────────────────────────

@dataclass
class FlashcardDto:
    id: int
    front: str
    back: str
    hint: str
    deck_id: int

    @staticmethod
    def from_model(fc) -> FlashcardDto:
        return FlashcardDto(
            id=fc.id,
            front=fc.front,
            back=fc.back,
            hint=fc.hint,
            deck_id=fc.deck_id,
        )


@dataclass
class DeckDto:
    id: int
    title: str
    description: str
    is_public: bool
    is_generated: bool
    owner_id: int
    card_count: int

    @staticmethod
    def from_model(deck) -> DeckDto:
        return DeckDto(
            id=deck.id,
            title=deck.title,
            description=deck.description,
            is_public=deck.is_public,
            is_generated=deck.is_generated,
            owner_id=deck.owner_id,
            card_count=deck.get_card_count(),
        )


# ── Flashcard Results ─────────────────────────────────────────────────────────

@dataclass
class CreateFlashcardResult:
    success: bool
    flashcard: FlashcardDto | None = None
    error: str | None = None


@dataclass
class BulkCreateFlashcardsResult:
    success: bool
    flashcards: list[FlashcardDto] | None = None
    error: str | None = None


@dataclass
class UpdateFlashcardResult:
    success: bool
    flashcard: FlashcardDto | None = None
    error: str | None = None


@dataclass
class DeleteFlashcardResult:
    success: bool
    error: str | None = None


@dataclass
class GetFlashcardResult:
    success: bool
    flashcard: FlashcardDto | None = None
    error: str | None = None


@dataclass
class ListFlashcardsResult:
    success: bool
    flashcards: list[FlashcardDto] = field(default_factory=list)
    error: str | None = None


# ── Deck Results ──────────────────────────────────────────────────────────────

@dataclass
class CreateDeckResult:
    success: bool
    deck: DeckDto | None = None
    error: str | None = None


@dataclass
class UpdateDeckResult:
    success: bool
    deck: DeckDto | None = None
    error: str | None = None


@dataclass
class DeleteDeckResult:
    success: bool
    error: str | None = None


@dataclass
class GetDeckResult:
    success: bool
    deck: DeckDto | None = None
    error: str | None = None


@dataclass
class ListDecksResult:
    success: bool
    decks: list[DeckDto] = field(default_factory=list)
    error: str | None = None