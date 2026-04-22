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

# Study context

@dataclass(frozen=True)
class StudySessionComplete(DomainEvent):
    session_id: int
    learner_id: int
    deck_id: int
    xp_earned: int
    cards_studied: int

@dataclass(frozen=True)
class LevelUpOccurred(DomainEvent):
    learner_id: int
    old_level_code: str | None
    new_level_code: str

@dataclass(frozen=True)
class CardMastered(DomainEvent):
    learner_id: int
    flashcard_id: int
