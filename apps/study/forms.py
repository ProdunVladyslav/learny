from django import forms

from apps.study.constants import StudyMode


# ── Start Session ─────────────────────────────────────────────────────────────

class StartStudySessionForm(forms.Form):
    """
    POSTed when the learner clicks "Start studying".

    deck_id       – which deck to study
    mode          – 'spaced' | 'cram'  (see StudyMode constants)
    cards_target  – optional cap on the number of cards queued for this session
    """
    MODE_CHOICES = [(m, m) for m in StudyMode.values]   # e.g. [('spaced', 'spaced'), ('cram', 'cram')]

    deck_id      = forms.IntegerField()
    mode         = forms.ChoiceField(choices=MODE_CHOICES)
    cards_target = forms.IntegerField(required=False, min_value=1)


# ── Submit Answer ─────────────────────────────────────────────────────────────

class SubmitAnswerForm(forms.Form):
    """
    POSTed after the learner reveals the answer and taps one of the four
    self-rating buttons.

    session_id    – active session
    flashcard_id  – card that was just answered
    question_type – e.g. 'front_to_back', 'multiple_choice', …
    rating        – 0 Blackout | 1 Hard | 2 Good | 3 Easy
    response_ms   – optional wall-clock time the learner took to answer
    """
    RATING_CHOICES = [
        (0, 'Blackout'),
        (1, 'Hard'),
        (2, 'Good'),
        (3, 'Easy'),
    ]

    session_id    = forms.IntegerField()
    flashcard_id  = forms.IntegerField()
    question_type = forms.CharField(max_length=50)
    rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    response_ms   = forms.IntegerField(required=False, min_value=0)


# ── Close Session ─────────────────────────────────────────────────────────────

class CloseStudySessionForm(forms.Form):
    """
    POSTed when the learner finishes (or abandons) a session.

    session_id – session to close
    """
    session_id = forms.IntegerField()


# ── Daily Review filter ───────────────────────────────────────────────────────

class GetDailyReviewForm(forms.Form):
    """
    GET params for the daily-review summary panel.

    deck_id – optional; when omitted, all decks are included
    """
    deck_id = forms.IntegerField(required=False)