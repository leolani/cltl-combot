import uuid
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Iterable, Callable

from cltl.combot.infra.di_container import DIContainer
from cltl.combot.infra.time_util import timestamp_now


class TopicError(ValueError):
    pass


@dataclass
class EventMetadata:
    timestamp: int = field(default_factory=timestamp_now)
    offset: int = -1
    topic: str = ""
    tenant: Optional[str] = None
    scenario_id: Optional[str] = None

    @classmethod
    def with_(cls, metadata, timestamp: int = None, offset: int = None, topic: str = None,
              tenant: str = None, scenario_id: str = None) -> "EventMetadata":
        new_timestamp = timestamp if timestamp is not None else metadata.timestamp
        new_offset = offset if offset is not None else metadata.offset
        new_topic = topic if topic is not None else metadata.topic
        new_tenant = tenant if tenant is not None else metadata.tenant
        if scenario_id is not None:
            new_scenario = scenario_id if scenario_id else None
        else:
            new_scenario = metadata.scenario_id

        return cls(new_timestamp, new_offset, new_topic, new_tenant, new_scenario)


PAYLOAD = TypeVar("PAYLOAD")


@dataclass
class Event(Generic[PAYLOAD]):
    id: str
    payload: PAYLOAD
    metadata: EventMetadata = field(default_factory=EventMetadata)

    @classmethod
    def for_payload(cls, payload: PAYLOAD, source: "Event" = None) -> "Event":
        event = cls(str(uuid.uuid4()), payload)

        if source:
            return Event.with_source(event, source)

        return event

    @classmethod
    def for_scenario_payload(cls, scenario_id: str, payload: PAYLOAD, source: "Event" = None) -> "Event":
        event = cls(str(uuid.uuid4()), payload)

        if source:
            event = Event.with_source(event, source)

        return Event.with_scenario(event, scenario_id)

    @classmethod
    def with_topic(cls, event: "Event", topic: str) -> "Event":
        if hasattr(event.metadata, 'topic') and event.metadata.topic == topic:
            return event

        return cls(event.id, event.payload, EventMetadata.with_(event.metadata, topic=topic))

    @classmethod
    def with_tenant(cls, event: "Event", tenant: str) -> "Event":
        if (hasattr(event, 'tenant') and tenant == event.metadata.tenant):
            return event

        metadata = EventMetadata.with_(event.metadata, tenant=tenant)

        return cls(event.id, event.payload, metadata)

    @classmethod
    def with_scenario(cls, event: "Event", scenario_id: str) -> "Event":
        if (hasattr(event, 'scenario_id') and scenario_id == event.metadata.scenario_id):
            return event

        metadata = EventMetadata.with_(event.metadata, scenario_id=scenario_id)

        return cls(event.id, event.payload, metadata)

    @classmethod
    def with_source(cls, event: "Event", source: "Event") -> "Event":
        if (hasattr(event, 'tenant') and hasattr(source, 'tenant')
                and event.metadata.tenant == source.metadata.tenant
                and (hasattr(event, 'scenario_id') and hasattr(source, 'scenario_id')
                and event.metadata.scenario_id == source.metadata.scenario_id)):
            return event

        metadata = EventMetadata.with_(event.metadata, tenant=source.metadata.tenant, scenario_id=source.metadata.scenario_id)

        return cls(event.id, event.payload, metadata)

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
