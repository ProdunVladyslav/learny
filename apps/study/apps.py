from django.apps import AppConfig


class StudyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.study'

    def ready(self) -> None:
        # Local imports — models are guaranteed to be loaded at this point.
        from shared.domain_events import FlashcardAddedToDeck
        from shared.event_bus import EventBus
        from apps.study.listeners.on_flashcard_added import on_flashcard_added

        EventBus.subscribe(FlashcardAddedToDeck, on_flashcard_added)
