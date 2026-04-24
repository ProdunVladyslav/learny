from apps.accounts.forms import CreateLanguageLearnerForm
from apps.accounts.repositories import LanguageLearnerRepository
from apps.accounts.use_cases.language_learners import CreateLanguageLearnerUseCase
from apps.decks.repositories import DeckRepository
from apps.decks.results import FlashcardDto
from apps.study.domain_services.card_progress_initialization_service import CardProgressInitializationService
from apps.study.forms import StartStudySessionForm
from apps.study.models import StudySession
from apps.study.repositories import StudySessionRepository, CardProgressRepository
from apps.study.results import StartSessionResult
from shared.domain_events import SessionStarted


class StartStudySessionUseCase:
    def __init__(
        self,
        session_repo:   StudySessionRepository,
        progress_repo:  CardProgressRepository,
        deck_repo:      DeckRepository,
        learner_repo:   LanguageLearnerRepository,
        create_learner: CreateLanguageLearnerUseCase,
    ):
        self.session_repo   = session_repo
        self.progress_repo  = progress_repo
        self.deck_repo      = deck_repo
        self.learner_repo   = learner_repo
        self.create_learner = create_learner

    def execute(self, user, form: StartStudySessionForm) -> StartSessionResult:
        if not form.is_valid():
            return StartSessionResult(success=False, error=form.errors)

        deck_id      = form.cleaned_data['deck_id']
        mode         = form.cleaned_data['mode']
        cards_target = form.cleaned_data.get('cards_target')

        # ── 1. resolve deck ───────────────────────────────────────────────────7530
        deck = self.deck_repo.get_by_id(deck_id)
        if deck is None:
            return StartSessionResult(success=False, error='Deck not found.')

        language_to_code   = deck.language_to_code
        language_from_code = deck.language_from_code  # may be None

        # ── 2. resolve LanguageLearner for this user + language pair ──────────
        learner = self.learner_repo.get_for_user_and_language(
            user=user,
            language_to_code=language_to_code,
        )

        if learner is None:
            learner_form = CreateLanguageLearnerForm(data={
                'language_to_code': language_to_code,
                'language_from_code': language_from_code,
            })
            result = self.create_learner.execute(user, learner_form)
            if not result.success:
                return StartSessionResult(success=False, error=result.error)
            # result.learner is a DTO — fetch the actual model instance
            learner = self.learner_repo.get_by_id(result.learner.id)

        # ── 3. ownership check ────────────────────────────────────────────────
        if not deck.is_owned_by(user):
            return StartSessionResult(success=False, error='Not your deck.')

        active = self.session_repo.get_active_for_learner(learner)
        if active:
            active.close()
            self.session_repo.save(active)

        # ── 4. ensure every deck flashcard has a CardProgress for this learner ─
        # Handles the case where cards were added before the learner existed
        # (the FlashcardAddedToDeck event only creates progress for existing learners).
        CardProgressInitializationService().initialize_for_deck_and_learner(deck_id, learner)

        # ── 5. build card queue: due first, then new ──────────────────────────
        due_qs = self.progress_repo.get_due_for_learner(learner).filter(
            flashcard__deck_id=deck_id
        )
        new_qs = self.progress_repo.get_new_for_learner(learner).filter(
            flashcard__deck_id=deck_id
        )

        due_cards = [p.flashcard for p in due_qs]
        new_cards = [p.flashcard for p in new_qs]
        all_cards = due_cards + new_cards

        if cards_target:
            all_cards = all_cards[:cards_target]

        if not all_cards:
            return StartSessionResult(success=False, error='No cards due for review.')

        # ── 6. create session ─────────────────────────────────────────────────
        session = StudySession.create(
            user=learner,
            deck=deck,
            mode=mode,
            cards_target=cards_target,
        )
        session = self.session_repo.save(session)

        self.session_repo.dispatch(SessionStarted(
            session_id=session.pk,
            learner_id=learner.pk,
            deck_id=deck_id,
            mode=mode,
        ))

        return StartSessionResult(
            success=True,
            session_id=session.pk,
            learner_id=learner.pk,
            cards=[FlashcardDto.from_model(c) for c in all_cards],
        )