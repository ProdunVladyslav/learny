from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class SubmitAnswerResult:
    success:          bool
    xp_awarded:       int = 0
    is_correct:       bool = False
    next_review_date: object = None        # date | None
    card_mastered:    bool = False
    error:            str | None = None
    events:           list = field(default_factory=list)


@dataclass
class StartSessionResult:
    success:    bool
    session_id: int | None = None
    learner_id: int | None = None
    cards:      list = field(default_factory=list)   # list[FlashcardDto]
    error:      str | None = None


@dataclass
class CloseSessionResult:
    success:          bool
    total_answers:    int = 0
    correct_answers:  int = 0
    accuracy_pct:     int = 0
    duration_seconds: float | None = None
    total_xp_earned:  int = 0
    error:            str | None = None
    events:           list = field(default_factory=list)

@dataclass
class DueCardDto:
    flashcard_id:  int
    front:         str
    back:          str
    deck_id:       int
    deck_title:    str
    next_review:   object   # date | None
    repetitions:   int
    strength:      int      # 0-100
    is_new:        bool

    @staticmethod
    def from_progress(progress) -> DueCardDto:
        return DueCardDto(
            flashcard_id=progress.flashcard.id,
            front=progress.flashcard.front,
            back=progress.flashcard.back,
            deck_id=progress.flashcard.deck_id,
            deck_title=progress.flashcard.deck.title,
            next_review=progress.next_review,
            repetitions=progress.repetitions,
            strength=progress.strength,
            is_new=progress.is_new,
        )


@dataclass
class DailyReviewSummaryResult:
    success:       bool
    due_count:     int = 0
    new_count:     int = 0
    total:         int = 0
    due_cards:     list[DueCardDto] = field(default_factory=list)
    by_deck:       dict = field(default_factory=dict)   # deck_title -> count
    error:         str | None = None