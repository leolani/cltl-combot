import json
import logging
from threading import RLock, Thread
from types import SimpleNamespace
from typing import Callable, Dict, Tuple, Set

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.pools import producers, connections
from kombu.serialization import register

from cltl.combot.infra.config import ConfigurationManager, ConfigurationContainer
from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.event.api import EventBusContainer, EventBus, Event

logger = logging.getLogger(__name__)


# Module-level variables for serialization functions (can be pickled)
_current_serializer_func = None
_current_deserializer_func = None

def _serialize_with_custom_func(obj):
    """Pickleable wrapper for custom serializer"""
    if _current_serializer_func:
        return _current_serializer_func(obj)
    else:
        return json.dumps(obj, default=vars)

def _deserialize_with_custom_func(data):
    """Pickleable wrapper for custom deserializer"""
    if _current_deserializer_func:
        return _current_deserializer_func(data)
    else:
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


class KombuEventBusContainer(EventBusContainer, ConfigurationContainer):
    logger.info("Initialized KombuEventBusContainer")

    @property
    @singleton
    def event_bus_serializer(self):
        """Return a serialization and deserialization function.

        serializer – A function that will be passed a python data structure and should return a string representing the
        serialized data.
        deserializer – A method that will be passed a string representing serialized data and should return a python
        data structure.

        Returns
        -------
        Any, Any
            A serialization and deserialization function.
        """
        return None, None

    @property
    def event_bus(self):
        return self.kombu_event_bus

    @property
    @singleton
    def kombu_event_bus(self):
        global _current_serializer_func, _current_deserializer_func

        serializer_func, deserializer_func = self.event_bus_serializer

        # Set module-level variables for the pickleable wrapper functions to use
        _current_serializer_func = serializer_func if serializer_func is not None else vars
        _current_deserializer_func = deserializer_func if deserializer_func is not None else lambda d: SimpleNamespace(**d)

        register('cltl-json',
                 _serialize_with_custom_func,
                 _deserialize_with_custom_func,
                 content_type='application/json',
                 content_encoding='utf-8')

        return KombuEventBus('cltl-json', self.config_manager)


class KombuEventBus(EventBus):
    def __init__(self, serializer: str, config_manager: ConfigurationManager):
        config = config_manager.get_config("cltl.event.kombu")
        server = config.get('server')
        exchange = config.get('exchange')
        self._compression = config.get('compression')
        self._serializer = serializer

        self._topic_lock = RLock()
        self.connection = Connection(server)
        self.exchange = Exchange(exchange, type="topic")

        self._tenant = config.get('tenant') if 'tenant' in config else None

        self._producer_topics: Set[str] = set()
        self._consumers: Dict[str, _EventBusConsumer] = {}
        self._handlers: Dict[str, Tuple[Callable, ...]] = {}

    def publish(self, topic: str, event: Event) -> None:
        if self._tenant and event.metadata.tenant and self._tenant != event.metadata.tenant:
            raise ValueError(f"Tenants don't match: {self._tenant} and {event.metadata}")

        if self._tenant and not event.metadata.tenant:
            event = Event.with_tenant(event, self._tenant)

        full_topic = f"{topic}.{event.metadata.tenant}" if event.metadata.tenant else topic

        self._producer_topics.add(full_topic)

        with connections[self.connection].acquire(block=True) as connection:
            with producers[connection].acquire(block=True) as producer:
                producer.publish(event,
                                 serializer=self._serializer,
                                 compression=self._compression,
                                 exchange=self.exchange,
                                 declare=[self.exchange],
                                 routing_key=full_topic)

    def subscribe(self, topic: str, handler: Callable[[Event], None]) -> None:
        with self._topic_lock:
            start_consumer = False
            if topic not in self._consumers:
                self._handlers[topic] = ()
                consumer = _EventBusConsumer(self.connection, self.exchange, self._serializer,
                                             topic, self._tenant, self._topic_handler(topic))
                self._consumers[topic] = consumer
                start_consumer = True

            self._handlers[topic] += (handler,)

            if start_consumer:
                self._consumers[topic].start()

        logger.info("Subscribed %s to topic %s", _format_name(handler), topic)

    def _topic_handler(self, topic: str):
        def handler(event):
            if topic in self._handlers:
                for h in self._handlers[topic]:
                    try:
                        h(Event.with_topic(event, topic))
                    except Exception:
                        logger.exception("Handler %s failed on topic %s", _format_name(h), topic)

        return handler

    def unsubscribe(self, topic: str, handler: Callable[[Event], None] = None) -> None:
        with self._topic_lock:
            if topic not in self._handlers:
                return
            elif handler:
                try:
                    self._handlers[topic] = tuple(h for h in self._handlers[topic] if h is not handler)
                    if len(self._handlers[topic]) == 0:
                        self._stop_consumer(topic)
                        logger.debug("Stopped EventBusConsumer for topic %s", topic)
                except ValueError as e:
                    raise ValueError("Failed to unregister " + _format_name(handler), e)
                logger.debug("Unsubscribed %s from topic %s", _format_name(handler), topic)
            else:
                self._stop_consumer(topic)
                logger.debug("Unsubscribed all handlers and stopped consumer for topic %s", topic)

    def _stop_consumer(self, topic):
        self._consumers[topic].should_stop = True
        self._consumers[topic].join()
        del self._consumers[topic]
        del self._handlers[topic]

    def close(self):
        """Clean up all consumers and close connections"""
        with self._topic_lock:
            for topic in list(self._consumers.keys()):
                self._stop_consumer(topic)
            self.connection.close()

    @property
    def topics(self):
        return tuple(self._consumers.keys() | self._producer_topics)


class _EventBusConsumer(ConsumerMixin, Thread):
    def __init__(self, connection, exchange, serializer, topic, tenant, callback):
        super().__init__(name=f"EventBusConsumer-{topic}-{_format_name(callback)}" + topic)
        self.connection = connection
        self.serializer = serializer
        self.topic = topic
        self.callback = callback

        full_topic = f"{topic}.{tenant}" if tenant else topic
        routing = f"{topic}.{tenant}" if tenant else f"{topic}.#"
        self.queue = Queue(full_topic, exchange, routing_key=routing, auto_delete=True)

    def get_consumers(self, Consumer, channel):
        return [Consumer([self.queue], accept=[self.serializer], callbacks=[self.on_message])]

    def on_message(self, body, message):
        logger.debug("Received message: %s", body)
        self.callback(body)
        message.ack()


def _format_name(handler: Callable[[Event], None]) -> str:
    return (handler.__self__.__class__.__name__ + "." if hasattr(handler, "im_class") else "") + handler.__name__