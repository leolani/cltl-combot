import json
import logging
from types import SimpleNamespace

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.pools import producers, connections
from threading import RLock, Thread
from typing import Callable, Dict, Tuple, Set
from kombu.serialization import register

from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.config import ConfigurationManager, ConfigurationContainer
from cltl.combot.infra.event import EventBusContainer, EventBus, Event

logger = logging.getLogger(__name__)


class KombuEventBusContainer(EventBusContainer, ConfigurationContainer):
    logger.info("Initialized KombuEventBusContainer")

    @property
    @singleton
    def event_bus(self):
        register('cltl-json',
                 lambda x: json.dumps(x, default=vars),
                 lambda x: json.loads(x, object_hook=lambda d: SimpleNamespace(**d)),
                 content_type='application/json',
                 content_encoding='utf-8')

        return KombuEventBus('cltl-json', self.config_manager)


class KombuEventBus(EventBus):
    def __init__(self, serializer: str, config_manager: ConfigurationManager):
        config = config_manager.get_config("cltl.event.kombu")
        server = config.get('server')
        exchange = config.get('exchange')
        exchange_type = config.get('type')
        self._compression = config.get('compression')
        self._serializer = serializer

        self._topic_lock = RLock()
        self.connection = Connection(server)
        self.exchange = Exchange(exchange, type=exchange_type)

        self._producer_topics: Set[str] = set()
        self._consumers: Dict[str, _EventBusConsumer] = {}
        self._handlers: Dict[str, Tuple[Callable, ...]] = {}

    def publish(self, topic: str, event: Event) -> None:
        self._producer_topics.add(topic)

        with connections[self.connection].acquire(block=True) as connection:
            with producers[connection].acquire(block=True) as producer:
                producer.publish(event,
                                 serializer=self._serializer,
                                 compression=self._compression,
                                 exchange=self.exchange,
                                 declare=[self.exchange],
                                 routing_key=topic)

    def subscribe(self, topic, handler: Callable[[Event], None]) -> None:
        with self._topic_lock:
            start_consumer = False
            if topic not in self._consumers:
                self._handlers[topic] = ()
                consumer = _EventBusConsumer(self.connection, self.exchange, self._serializer,
                                             topic, self._topic_handler(topic))
                self._consumers[topic] = consumer
                start_consumer = True

            self._handlers[topic] += (handler,)

            if start_consumer:
                self._consumers[topic].start()

        logger.info("Subscribed %s to topic %s", _format_name(handler), topic)

    def _topic_handler(self, topic: str):
        def handler(event):
            if topic in self._handlers:
                for handl in self._handlers[topic]:
                    handl(Event.with_topic(event, topic))

        return handler

    def unsubscribe(self, topic: str, handler: Callable[[Event], None] = None) -> None:
        with self._topic_lock:
            if topic not in self._handlers:
                return
            elif handler:
                try:
                    self._handlers[topic] = tuple(h for h in self._handlers if h is not handler)
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

    @property
    def topics(self):
        return tuple(self._consumers.keys() | self._producer_topics)


class _EventBusConsumer(ConsumerMixin, Thread):
    def __init__(self, connection, exchange, serializer, topic, callback):
        super().__init__(name=f"EventBusConsumer-{topic}-{_format_name(callback)}" + topic)
        self.connection = connection
        self.serializer = serializer
        self.topic = topic
        self.callback = callback
        self.queue = Queue(topic, exchange, routing_key=topic)

    def get_consumers(self, Consumer, channel):
        return [Consumer([self.queue], accept=[self.serializer], callbacks=[self.on_message])]

    def on_message(self, body, message):
        logger.debug("Received message: %s", body)
        self.callback(body)
        message.ack()


def _format_name(handler: Callable[[Event], None]) -> str:
    return (handler.__self__.__class__.__name__ + "." if hasattr(handler, "im_class") else "") + handler.__name__