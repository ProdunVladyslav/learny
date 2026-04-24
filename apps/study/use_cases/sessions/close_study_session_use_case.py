from apps.accounts.repositories import LanguageLearnerRepository
from apps.study.forms import CloseStudySessionForm
from apps.study.repositories import StudySessionRepository
from apps.study.results import CloseSessionResult


class CloseStudySessionUseCase:
    def __init__(self, session_repo: StudySessionRepository, learner_repo: LanguageLearnerRepository):
        self.session_repo = session_repo
        self.learner_repo = learner_repo

    def execute(self, user, form: CloseStudySessionForm) -> CloseSessionResult:
        if not form.is_valid():
            return CloseSessionResult(success=False, error=form.errors)

        session_id = form.cleaned_data['session_id']

        # ── guards ────────────────────────────────────────────────────────────
        session = self.session_repo.get_by_id(session_id)
        if session is None:
            return CloseSessionResult(success=False, error='Session not found.')

        learner = self.learner_repo.get_by_id(session.user_id)
        if learner is None or learner.user_id != user.pk:
            return CloseSessionResult(success=False, error='Not your session.')

        if session.is_finished:
            return CloseSessionResult(success=False, error='Session already closed.')

        # ── close ─────────────────────────────────────────────────────────────
        session.close()
        self.session_repo.save(session)

        return CloseSessionResult(success=True, session_id=session.pk)