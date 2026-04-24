"""
apps/study/services/card_progress_initialization_service.py

Domain service — creates CardProgress + CardXPRecord for every LanguageLearner
who is studying the language of a newly added flashcard.

Why a domain service and not inline in the listener?
  - Testable without Django signals or EventBus wiring
  - Reusable: bulk-import flows can call it directly
  - Keeps the listener paper-thin (pure dispatch, no logic)
"""
from datetime import datetime, date

from apps.accounts.models import LanguageLearner
from apps.study.models import CardProgress
from apps.study.models.card_xp_record import CardXPRecord


class CardProgressInitializationService:
    def initialize_for_flashcard(
        self,
        flashcard_id: int,
        language_to_id: int,
    ) -> list[CardProgress]:
        import inspect
        print("RUNNING FROM:", inspect.getfile(self.__class__))
        """
        Creates missing CardProgress + CardXPRecord records.
        Returns the list of CardProgress objects that were newly created
        (already-existing ones are excluded — useful for logging / metrics).
        """
        learners = LanguageLearner.objects.filter(
            language_to_id=language_to_id,
            is_active=True,
        )

        created_progresses: list[CardProgress] = []

        for learner in learners:
            progress, created = CardProgress.objects.get_or_create(
                user=learner,
                flashcard_id=flashcard_id,
                defaults={'next_review': date.today()},
            )

            # Always ensure the XP record exists — safe to call on existing progress.
            CardXPRecord.get_or_create_record(progress)

            if created:
                created_progresses.append(progress)

        return created_progresses

    def initialize_for_deck_and_learner(
        self,
        deck_id: int,
        learner: LanguageLearner,
    ) -> list[CardProgress]:
        """
        Ensures every flashcard in a deck has a CardProgress + CardXPRecord for
        the given learner. Idempotent — safe to call even if records already exist.

        Called at session-start time to handle the case where the learner was
        created after the cards were added (so the FlashcardAddedToDeck event
        had no learner to target).
        """
        from apps.decks.models import Flashcard

        flashcards = Flashcard.objects.filter(deck_id=deck_id)
        created_progresses: list[CardProgress] = []

        for flashcard in flashcards:
            progress, created = CardProgress.objects.get_or_create(
                user=learner,
                flashcard=flashcard,
                defaults={'next_review': date.today()},
            )
            CardXPRecord.get_or_create_record(progress)
            if created:
                created_progresses.append(progress)

        return created_progresses