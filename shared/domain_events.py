from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now, init=False)

# Accounts context
@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: int
    email: str
    username: str

@dataclass(frozen=True)
class UserOnboarded(DomainEvent):
    user_id: int
    learner_id: int
    language_it: int


@dataclass(frozen=True)
class FlashcardAddedToDeck(DomainEvent):
    """
    Fired after a Flashcard is persisted to a Deck.

    Carries the IDs needed by downstream listeners so they never have to
    re-fetch the Flashcard or Deck themselves — the event is self-contained.

    language_from_id  — nullable (mirrors Deck.language_from which is optional).
    language_to_id    — always present; this is the language being studied.
    """
    flashcard_id: int
    deck_id: int
    language_to_id: int
    language_from_id: int | None

# Study context

@dataclass(frozen=True)
class CardAnswered(DomainEvent):
    session_id:    int
    flashcard_id:  int
    learner_id:    int
    is_correct:    bool
    response_ms:   int | None
    question_type: str


@dataclass(frozen=True)
class CardMastered(DomainEvent):
    flashcard_id: int
    learner_id:   int
    repetitions:  int
    ease_factor:  float


@dataclass(frozen=True)
class SessionStarted(DomainEvent):
    session_id: int
    learner_id: int
    deck_id:    int
    mode:       str


@dataclass(frozen=True)
class SessionCompleted(DomainEvent):
    session_id:       int
    learner_id:       int
    deck_id:          int
    total_answers:    int
    correct_answers:  int
    duration_seconds: float | None
    total_xp_earned:  int


@dataclass(frozen=True)
class LevelUpOccurred(DomainEvent):
    learner_id:     int
    old_level_code: str | None
    new_level_code: str


@dataclass(frozen=True)
class XPAwarded(DomainEvent):
    learner_id:  int
    amount:      int
    flashcard_id: int
    session_id:  int

