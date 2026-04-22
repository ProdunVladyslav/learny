from dataclasses import dataclass
from datetime import date, timedelta

from apps.study.models import CardProgress


@dataclass
class SM2Result:
    repetitions:   int
    ease_factor:   float
    interval_days: int
    next_review:   date

class SpacedRepetitionService:
    """
    Implements the SM-2 spaced repetition algorithm.
    Pure logic — no DB, no ORM, no imports from models.
    Input: current progress state + answer quality (0-5)
    Output: new progress values
    """

    def calculate(self, progress: CardProgress, quality: int) -> SM2Result:
        """
        quality: 0-5 where 5 = perfect, 0 = complete blackout
        SM-2 minimum passing quality is 3.
        """
        if quality < 3:
            return SM2Result(
                repetitions=0,
                ease_factor=max(1.3, progress.ease_factor - 0.2),
                interval_days=1,
                next_review=date.today() + timedelta(days=1),
            )

        new_ease = progress.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease = max(1.3, new_ease)

        if progress.repetitions == 0:
            interval = 1
        elif progress.repetitions == 1:
            interval = 6
        else:
            interval = round(progress.interval_days * new_ease)

        return SM2Result(
            repetitions=progress.repetitions + 1,
            ease_factor=new_ease,
            interval_days=interval,
            next_review=date.today() + timedelta(days=interval),
        )