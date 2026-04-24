from apps.accounts.repositories import LanguageLearnerRepository
from apps.decks.repositories import DeckRepository
from apps.study.constants import StudyMode
from apps.study.domain_services import (
    SpacedRepetitionService,
    XPAwardService, QuestionTypeSelectorService,
)
from apps.study.forms import SubmitAnswerForm
from apps.study.models import CardAnswer, CardXPRecord
from apps.study.repositories import StudySessionRepository, CardProgressRepository
from apps.study.results import SubmitAnswerResult
from shared.domain_events import CardAnswered, CardMastered, XPAwarded
from shared.value_objects import ResponseTime
from shared.value_objects.answer_rating_value_object import AnswerRating


class SubmitAnswerUseCase:
    def __init__(
        self,
        session_repo:  StudySessionRepository,
        progress_repo: CardProgressRepository,
        deck_repo:     DeckRepository,
        learner_repo:  LanguageLearnerRepository,
        srs:           SpacedRepetitionService,
        xp_svc:        XPAwardService,
        qt_selector:   QuestionTypeSelectorService,
    ):
        self.session_repo  = session_repo
        self.progress_repo = progress_repo
        self.deck_repo     = deck_repo
        self.learner_repo  = learner_repo
        self.srs           = srs
        self.xp_svc        = xp_svc
        self.qt_selector   = qt_selector

    def execute(self, user, form: SubmitAnswerForm) -> SubmitAnswerResult:
        if not form.is_valid():
            return SubmitAnswerResult(success=False, error=form.errors)

        session_id    = form.cleaned_data['session_id']
        flashcard_id  = form.cleaned_data['flashcard_id']
        question_type = form.cleaned_data['question_type']
        rating        = form.cleaned_data['rating']
        response_ms   = form.cleaned_data.get('response_ms')

        events = []

        try:
            answer = AnswerRating(rating)
        except ValueError as e:
            return SubmitAnswerResult(success=False, error=str(e))

        is_correct = answer.is_correct
        quality    = answer.sm2_quality

        # ── 1. guards ─────────────────────────────────────────────────────────
        session = self.session_repo.get_by_id(session_id)
        if session is None:
            return SubmitAnswerResult(success=False, error='Session not found.')
        if session.is_finished:
            return SubmitAnswerResult(success=False, error='Session already closed.')

        # resolve LanguageLearner — session.user IS the learner FK
        learner = session.user
        if learner.user_id != user.pk:
            return SubmitAnswerResult(success=False, error='Not your session.')

        flashcard = self.deck_repo.get_flashcard_by_id(flashcard_id)
        if flashcard is None:
            return SubmitAnswerResult(success=False, error='Flashcard not found.')

        # ── 2. record answer ──────────────────────────────────────────────────
        CardAnswer.create(
            session=session,
            flashcard=flashcard,
            question_type=question_type,
            is_correct=is_correct,
            response_ms=response_ms,
        )
        events.append(CardAnswered(
            session_id=session.pk,
            flashcard_id=flashcard_id,
            learner_id=learner.pk,
            is_correct=is_correct,
            response_ms=response_ms,
            question_type=question_type,
        ))

        # ── 3. spaced repetition OR cram ──────────────────────────────────────
        progress = self.progress_repo.get_or_create_for(learner=learner, flashcard=flashcard)

        if session.mode == StudyMode.CRAM:
            new_ease = progress.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            progress.apply_cram(ease_factor=new_ease)
            self.progress_repo.save_fields(progress, ['ease_factor', 'last_seen_at'])
            next_review_date = progress.next_review
        else:
            sm2 = self.srs.calculate(progress, quality)
            progress.apply_spaced(
                repetitions=sm2.repetitions,
                ease_factor=sm2.ease_factor,
                interval_days=sm2.interval_days,
                next_review=sm2.next_review,
            )
            self.progress_repo.save_spaced_repetition(progress)
            next_review_date = sm2.next_review

            if progress.is_mastered:
                events.append(CardMastered(
                    flashcard_id=flashcard_id,
                    learner_id=learner.pk,
                    repetitions=sm2.repetitions,
                    ease_factor=sm2.ease_factor,
                ))

        # ── 4. select next question type for this card ────────────────────────
        next_qt_selection = self.qt_selector.select(progress)

        # ── 5. XP — mode is the question_type that was just answered ─────────
        rt = ResponseTime(response_ms) if response_ms is not None else None
        raw_xp = self.xp_svc.calculate_xp(
            is_correct=is_correct,
            response_time=rt,
            mode=question_type,
        ) if rt else (
            round(self.xp_svc.BASE_XP * self.xp_svc.MODE_MULTIPLIERS.get(question_type, 1.0))
            if is_correct else 0
        )

        xp_record = CardXPRecord.get_or_create_record(progress)
        xp_result = self.xp_svc.award(xp_record=xp_record, learner=learner, amount=raw_xp)

        if xp_result.actual_xp_awarded > 0:
            events.append(XPAwarded(
                learner_id=learner.pk,
                amount=xp_result.actual_xp_awarded,
                flashcard_id=flashcard_id,
                session_id=session_id,
            ))
        if xp_result.level_event:
            events.append(xp_result.level_event)

        # ── 6. atomic save ────────────────────────────────────────────────────
        self.progress_repo.save_with_xp(progress)
        self.session_repo.save_learner(learner)
        self.session_repo.dispatch_all(events)

        return SubmitAnswerResult(
            success=True,
            xp_awarded=xp_result.actual_xp_awarded,
            is_correct=is_correct,
            next_review_date=next_review_date,
            card_mastered=progress.is_mastered,
            next_question_type=next_qt_selection.question_type,
            next_question_tier=next_qt_selection.tier,
            events=events,
        )