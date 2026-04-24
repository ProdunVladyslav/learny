"""
apps/study/listeners/on_flashcard_added.py

Thin listener — receives FlashcardAddedToDeck and delegates to the domain
service. No logic lives here; this is pure dispatch.
"""

import logging

from apps.study.domain_services import CardProgressInitializationService
from shared.domain_events import FlashcardAddedToDeck

logger = logging.getLogger(__name__)


def on_flashcard_added(event: FlashcardAddedToDeck) -> None:
    """
    Creates CardProgress + CardXPRecord for every active LanguageLearner
    studying the deck's target language.

    Runs synchronously inside the same request/transaction as card creation.
    If you need async execution, wrap this in Celery and publish from there.
    """
    service = CardProgressInitializationService()

    created = service.initialize_for_flashcard(
        flashcard_id=event.flashcard_id,
        language_to_id=event.language_to_id,
    )

    if created:
        logger.debug(
            "Initialized %d CardProgress records for flashcard_id=%d (deck_id=%d)",
            len(created),
            event.flashcard_id,
            event.deck_id,
        )