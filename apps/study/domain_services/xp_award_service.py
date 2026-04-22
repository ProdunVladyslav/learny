# apps/study/domain_services/xp_award_service.py
from dataclasses import dataclass
from apps.accounts.models import LanguageLearner
from apps.study.models import CardXPRecord
from shared.domain_events import LevelUpOccurred
from shared.value_objects import XPAmount, ResponseTime


@dataclass
class XPAwardResult:
    actual_xp_awarded: int
    level_event:       LevelUpOccurred | None


class XPAwardService:
    BASE_XP       = 10
    CORRECT_BONUS = 5
    FAST_BONUS    = 3

    def calculate_xp(self, is_correct: bool, response_time: ResponseTime) -> int:
        """Pure calculation — no DB, no side effects."""
        if not is_correct:
            return 0
        xp = self.BASE_XP + self.CORRECT_BONUS
        if response_time.is_fast:
            xp += self.FAST_BONUS
        return xp

    def award(
        self,
        xp_record: CardXPRecord,
        learner:   LanguageLearner,
        amount:    int,
    ) -> XPAwardResult:
        """
        Coordinates XP application across two aggregates.
        Does NOT save — use case responsible.
        """
        from apps.languages.models import ProficiencyLevel

        # 1. apply per-card cap
        actual_xp = xp_record.add_xp(amount)

        # 2. clamp total XP
        raw_xp    = max(0, min(XPAmount.MAX, learner.xp + actual_xp))
        new_xp    = XPAmount(value=raw_xp).value

        # 3. check level change
        old_level = learner.current_level
        new_level = ProficiencyLevel.get_for_xp(new_xp)

        # 4. mutate model — only direct field assignment, no logic
        learner.xp            = new_xp
        learner.current_level = new_level

        # 5. build event if level changed
        level_event = None
        if old_level != new_level:
            level_event = LevelUpOccurred(
                learner_id=learner.pk,
                old_level_code=old_level.code if old_level else None,
                new_level_code=new_level.code if new_level else '',
            )

        return XPAwardResult(
            actual_xp_awarded=actual_xp,
            level_event=level_event,
        )