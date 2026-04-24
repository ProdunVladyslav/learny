# apps/study/domain_services/question_type_selector.py
import random
from dataclasses import dataclass

from apps.study.constants import QuestionType
from apps.study.models import CardProgress


@dataclass
class QuestionTypeSelection:
    question_type: str
    tier:          str
    reason:        str


class QuestionTypeSelectorService:
    """
    Selects the most appropriate question type for a given CardProgress state.

    Active question types: TRUE_FALSE, MULTIPLE_CHOICE, MATCH, WRITE_DOWN.
    FILL_BLANK and LISTENING are excluded until implemented.

    Difficulty ladder:
        True/False → Multiple choice → Match → Write down

    Tier thresholds:
        new         → true/false or multiple choice
        0–49        → multiple choice  (superficial knowledge)
        50–79       → match            (recognition solidifying)
        80+ & not mastered → multiple choice  (strong but not ready to write)
        80+ & mastered     → write down
    """

    RECOGNITION_THRESHOLD = 50   # below → superficial
    STRONG_THRESHOLD      = 80   # below → recognition; above → mastered gate

    _TIER_POOLS: dict[str, list[str]] = {
        'new':        [QuestionType.TRUE_FALSE, QuestionType.MULTIPLE_CHOICE],
        'superficial':[QuestionType.MULTIPLE_CHOICE],
        'recognition':[QuestionType.MATCH],
        'strong':     [QuestionType.MULTIPLE_CHOICE],  # holding pattern until WRITE_DOWN
        'mastered':   [QuestionType.WRITE_DOWN],
    }

    def select(self, progress: CardProgress) -> QuestionTypeSelection:
        """Pure calculation — no DB, no side effects."""
        tier, reason = self._resolve_tier(progress)
        question_type = self._pick_from_pool(tier)
        return QuestionTypeSelection(
            question_type=question_type,
            tier=tier,
            reason=reason,
        )

    def _resolve_tier(self, progress: CardProgress) -> tuple[str, str]:
        if progress.is_new:
            return 'new', "Card never seen — introduce with easy recognition"

        strength = progress.strength

        if strength < self.RECOGNITION_THRESHOLD:
            return (
                'superficial',
                f"Strength {strength} < {self.RECOGNITION_THRESHOLD} — knowledge superficial",
            )

        if strength < self.STRONG_THRESHOLD:
            return (
                'recognition',
                f"Strength {strength} in {self.RECOGNITION_THRESHOLD}–{self.STRONG_THRESHOLD - 1} — recognition tier",
            )

        if progress.is_mastered:
            return (
                'mastered',
                f"Strength {strength}, is_mastered=True — full writing challenge",
            )

        return (
            'strong',
            f"Strength {strength} ≥ {self.STRONG_THRESHOLD} but not yet mastered — holding on multi-choice",
        )

    def _pick_from_pool(self, tier: str) -> str:
        pool = self._TIER_POOLS[tier]
        return random.choice(pool) if len(pool) > 1 else pool[0]