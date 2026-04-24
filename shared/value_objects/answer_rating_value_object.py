from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerRating:
    value: int   # 0-3 from user

    @property
    def is_correct(self) -> bool:
        return self.value >= 2       # Good or Easy = correct

    def __post_init__(self):
        if self.value not in (0, 1, 2, 3):
            raise ValueError(f'AnswerRating must be 0-3, got {self.value}')

    @property
    def sm2_quality(self) -> int:
        # maps 0-3 user rating → 0-5 SM-2 quality
        return {
            0: 0,   # Blackout → 0
            1: 2,   # Hard     → 2 (wrong but familiar)
            2: 4,   # Good     → 4 (correct with hesitation)
            3: 5,   # Easy     → 5 (perfect recall)
        }[self.value]