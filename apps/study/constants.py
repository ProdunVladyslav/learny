# study/constants.py  ← new file
from enum import Enum

from django.db import models


class StudyMode(models.TextChoices):
    SPACED = 'spaced', 'Spaced'
    CRAM   = 'cram',   'Cram'

class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'multiple_choice', 'Multiple choice'  # pick correct answer from 4 options
    WRITE_DOWN      = 'write_down',      'Write down'       # type the answer manually
    MATCH           = 'match',           'Match'            # pair words with translations
    TRUE_FALSE      = 'true_false',      'True / false'     # is this translation correct?
    LISTENING       = 'listening',       'Listening'        # hear audio, write or pick answer
    FILL_BLANK      = 'fill_blank',      'Fill in the blank' # complete the sentence

XP_LEVEL_THRESHOLDS: dict[str, tuple[int, int]] = {
    'A1': (0,     1000),
    'A2': (1001,  2500),
    'B1': (2501,  4500),
    'B2': (4501,  6500),
    'C1': (6501,  8500),
    'C2': (8501,  10000),
}

BASE_XP_CORRECT   = 25
BASE_XP_INCORRECT = -5
MAX_TIME_BONUS    = 15
FAST_RESPONSE_MS  = 2_000
SLOW_RESPONSE_MS  = 10_000
CARD_XP_CAP       = 100

MODE_MULTIPLIERS = {
    StudyMode.SPACED: 1.5,
    StudyMode.CRAM:   0.75,
}

def calculate_time_bonus(response_ms: int) -> int:
    if response_ms <= FAST_RESPONSE_MS:
        return MAX_TIME_BONUS
    if response_ms >= SLOW_RESPONSE_MS:
        return 0
    ratio = (SLOW_RESPONSE_MS - response_ms) / (SLOW_RESPONSE_MS - FAST_RESPONSE_MS)
    return round(MAX_TIME_BONUS * ratio)

def get_level_name_for_xp(xp: int) -> str:
    for level_name, (low, high) in XP_LEVEL_THRESHOLDS.items():
        if low <= xp <= high:
            return level_name
    return 'C2'


def calculate_accuracy(total: int, correct: int) -> float:
    """Pure function — no DB calls."""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)
