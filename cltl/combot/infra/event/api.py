from dataclasses import dataclass

from typing import TypeVar, Generic, Optional, Iterable, Callable

from cltl.combot.infra.di_container import DIContainer


class TopicError(ValueError):
    pass


@dataclass
class EventMetadata:
    timestamp: int
    offset: int
    topic: str

    def with_(self, timestamp: int = None, offset: int = None, topic: str = None) -> Optional["EventMetadata"]:
        new_timestamp = timestamp if timestamp is not None else self.timestamp
        new_offset = offset if offset is not None else self.offset
        new_topic = topic if topic is not None else self.topic
        return EventMetadata(new_timestamp, new_offset, new_topic)


T = TypeVar("T")
@dataclass
class Event(Generic[T]):
    id: str
    payload: T
    metadata: EventMetadata

    def with_topic(self, topic: str) -> Optional["Event"]:
        return Event(self.id, self.payload, self.metadata.with_(topic=topic))

    def __eq__(self, other):
        return self.id == other.id


class EventBus:
    """
    Supports publishing of and subscribing to events based on topics.

    Events published to a topic are delivered to all subscribers in the order
    of their arrival. Publishing and invocation of the subscribed handler
    can be asynchronous. Subscribers receive only events that arrive after they
    subscribed to a topic.
    """

    def publish(self, topic: str, event: Event) -> None:
        raise NotImplementedError()

    def subscribe(self, topic, handler: Callable[[Event], None]) -> None:
        raise NotImplementedError()

    def unsubscribe(self, topic: str, handler: Callable[[Event], None] = None) -> None:
        raise NotImplementedError()

    @property
    def topics(self) -> Iterable[str]:
        raise NotImplementedError()

    def has_topic(self, topic: str) -> bool:
        return topic in self.topics


class EventBusContainer(DIContainer):
    @property
    def event_bus(self) -> EventBus:
        raise ValueError("No EventBus configured")
