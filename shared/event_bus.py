from collections import defaultdict
from typing import Callable, Type

from shared.domain_events import DomainEvent


class EventBus:
    _listeners: dict[Type[DomainEvent], list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: Type[DomainEvent], listener: Callable):
        cls._listeners[event_type].append(listener)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        for listener in cls._listeners[type(event)]:
            listener(event)

    @classmethod
    def clear(cls) -> None:
        # used in tests to reset listeners
        cls._listeners.clear()