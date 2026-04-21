from django.db import transaction

from apps.accounts.models.language_learner import (
    LanguageLearner
)
from apps.study.constants import calculate_time_bonus, StudyMode, CARD_XP_CAP, BASE_XP_CORRECT, BASE_XP_INCORRECT, \
    MODE_MULTIPLIERS, get_level_name_for_xp, calculate_accuracy
from apps.study.models import CardXPRecord
from apps.study.models.study_session import StudySession


@transaction.atomic
def award_xp(
    learner: LanguageLearner,
    card,
    is_correct: bool,
    response_ms: int,
    mode: StudyMode,
    card_xp_cap: int = CARD_XP_CAP,
) -> dict:
    # 1. Calculate raw delta
    if is_correct:
        time_bonus = calculate_time_bonus(response_ms)
        raw_delta = BASE_XP_CORRECT + time_bonus
    else:
        raw_delta = BASE_XP_INCORRECT

    xp_delta = round(raw_delta * MODE_MULTIPLIERS[mode])

    # 2. Enforce per-card cap
    record = CardXPRecord.get_or_create_record(learner=learner, card=card)

    if record.is_cap_expired():
        record.reset_cap()

    if xp_delta > 0:
        xp_delta = min(xp_delta, record.remaining_xp_capacity(card_xp_cap))

    capped = xp_delta == 0 and is_correct

    # 3. Apply to learner and save
    levelled_up = learner.apply_xp_delta(xp_delta)
    learner.save(update_fields=['xp'])

    # 4. Apply to card record and save
    if xp_delta > 0:
        record.add_xp(xp_delta)
        record.save(update_fields=['total_xp_earned', 'last_studied_at'])

    return {
        'xp_delta':    xp_delta,
        'new_xp':      learner.xp,
        'level_name':  get_level_name_for_xp(learner.xp),
        'levelled_up': levelled_up,
        'card_xp_used': record.total_xp_earned,
        'card_xp_cap':  card_xp_cap,
        'card_capped':  capped,
    }

def get_session_stats(session: StudySession) -> dict:
    total   = session.card_answers.count()   # one query, reused everywhere
    correct = session.card_answers.filter(is_correct=True).count()
    return {
        'total':             total,
        'correct':           correct,
        'accuracy':          calculate_accuracy(total, correct),
        'has_reached_target': session.has_reached_target(total),
        'is_finished':       session.is_finished,
        'duration_seconds': session.duration_seconds,
    }