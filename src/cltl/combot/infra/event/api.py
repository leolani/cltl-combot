import uuid
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Iterable, Callable

from cltl.combot.infra.di_container import DIContainer
from cltl.combot.infra.time_util import timestamp_now


class TopicError(ValueError):
    pass


@dataclass
class EventMetadata:
    timestamp: int = timestamp_now()
    offset: int = -1
    topic: str = ""
    scenario_id: Optional[str] = None

    @classmethod
    def with_(cls, metadata, timestamp: int = None, offset: int = None, topic: str = None, scenario_id: str = None) -> Optional["EventMetadata"]:
        new_timestamp = timestamp if timestamp is not None else metadata.timestamp
        new_offset = offset if offset is not None else metadata.offset
        new_topic = topic if topic is not None else metadata.topic
        new_scenario_id = scenario_id if scenario_id is not None else metadata.scenario_id

        return cls(new_timestamp, new_offset, new_topic, new_scenario_id)


T = TypeVar("T")
@dataclass
class Event(Generic[T]):
    id: str
    payload: T
    metadata: EventMetadata = EventMetadata()

    @classmethod
    def for_payload(cls, payload: T, scenario_id: str = None) -> Optional["Event"]:
        event = cls(str(uuid.uuid4()), payload)

        return event.with_scenario_id(scenario_id) if scenario_id else event

    @classmethod
    def with_topic(cls, event, topic: str) -> Optional["Event"]:
        return cls(event.id, event.payload, EventMetadata.with_(event.metadata, topic=topic))

    @classmethod
    def with_scenario(cls, event, scenario_id: str) -> Optional["Event"]:
        return cls(event.id, event.payload, EventMetadata.with_(event.metadata, scenario_id=scenario_id))

    def __eq__(self, other):
        return other and self.id == other.id

    def __hash__(self):
        return hash(self.id) if self.id else hash("")


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
