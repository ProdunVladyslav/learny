"""
apps/study/container.py

Single source of truth for study-context dependency wiring.
Views call a factory method — they never instantiate repos or services directly.

Why a container class over a DI framework?
  - Zero external deps
  - All wiring visible in one file — no scanning magic
  - Each factory method is independently testable (swap a repo, inject a mock)
  - Stateless: every call returns a freshly wired instance (safe for Django's
    multi-threaded / multi-process request handling)
"""

from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.use_cases.language_learners import CreateLanguageLearnerUseCase
from apps.decks.repositories import DeckRepository
from apps.study.domain_services import (
    SpacedRepetitionService,
    XPAwardService,
    QuestionTypeSelectorService,
)
from apps.study.repositories import StudySessionRepository, CardProgressRepository
from apps.study.use_cases.sessions.close_study_session_use_case import CloseStudySessionUseCase
from apps.study.use_cases.sessions.get_daily_review_use_case import GetDailyReviewUseCase
from apps.study.use_cases.sessions.start_study_session_use_case import StartStudySessionUseCase
from apps.study.use_cases.sessions.submit_answer_use_case import SubmitAnswerUseCase


class StudyContainer:

    @staticmethod
    def get_daily_review() -> GetDailyReviewUseCase:
        return GetDailyReviewUseCase(
            progress_repo=CardProgressRepository(),
            learner_repo=LanguageLearnerRepository(),
        )

    @staticmethod
    def start_session() -> StartStudySessionUseCase:
        learner_repo = LanguageLearnerRepository()
        return StartStudySessionUseCase(
            session_repo=StudySessionRepository(),
            progress_repo=CardProgressRepository(),
            deck_repo=DeckRepository(),
            learner_repo=learner_repo,
            create_learner=CreateLanguageLearnerUseCase(learner_repo),
        )

    @staticmethod
    def submit_answer() -> SubmitAnswerUseCase:
        return SubmitAnswerUseCase(
            session_repo=StudySessionRepository(),
            progress_repo=CardProgressRepository(),
            deck_repo=DeckRepository(),
            learner_repo=LanguageLearnerRepository(),
            srs=SpacedRepetitionService(),
            xp_svc=XPAwardService(),
            qt_selector=QuestionTypeSelectorService(),
        )

    @staticmethod
    def close_session() -> CloseStudySessionUseCase:
        return CloseStudySessionUseCase(
            session_repo=StudySessionRepository(),
            learner_repo=LanguageLearnerRepository(),
        )