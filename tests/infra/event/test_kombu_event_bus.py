from types import SimpleNamespace

from kombu.serialization import register
import json

from unittest import mock

import logging
import sys
import unittest

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event.api import Event, EventMetadata
from cltl.combot.infra.event.kombu import KombuEventBus, KombuEventBusContainer
from cltl.combot.test.util import await_predicate

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


register('cltl-json',
         lambda x: json.dumps(x, default=vars),
         lambda x: json.loads(x, object_hook=lambda d: SimpleNamespace(**d)),
         content_type='application/json',
         content_encoding='utf-8')

class KombuEventBusTestCase(unittest.TestCase):

    counter = 0

    def get_id(self):
        KombuEventBusTestCase.counter += 1
        return str(KombuEventBusTestCase.counter)

    def setUp(self):
        config_manager = mock.create_autospec(ConfigurationManager)
        config_manager.get_config.return_value = {
            "server": "memory:///",
            "exchange": "cltl.combot",
            "type": "direct",
            "compression": "bzip2",
        }

        self.event_bus = KombuEventBus('cltl-json', config_manager)
        self.topic = "test topic - " + self.get_id()

    def tearDown(self) -> None:
        for topic in self.event_bus.topics:
            self.event_bus.unsubscribe(topic)

    def test_publish(self):
        event = Event.for_payload("test payload - " + self.get_id())
        self.event_bus.publish(self.topic, event)

        self.assertEqual([self.topic], [ t for t in self.event_bus.topics ])

    def test_subscribe(self):
        actual_events = []

        def handler(ev):
            actual_events.append(ev)

        event = Event.for_payload("test payload - " + self.get_id())

        self.event_bus.subscribe(self.topic, handler)
        self.event_bus.publish(self.topic, event)

        await_predicate(lambda: len(actual_events) > 0, "event received")

        self.assertEqual(1, len(actual_events))
        self.assertEqual(event, actual_events[0])

    def test_multiple_subscribers(self):
        actual_events = []

        def handler_one(ev):
            actual_events.append(ev)

        def handler_two(ev):
            actual_events.append(ev)

        event = Event.for_payload("test payload - " + self.get_id())

        self.event_bus.subscribe(self.topic, handler_one)
        self.event_bus.subscribe(self.topic, handler_two)
        self.event_bus.publish(self.topic, event)

        await_predicate(lambda: len(actual_events) > 1, "events received")

        self.assertEqual(2, len(actual_events))
        self.assertEqual(event, actual_events[0])
        self.assertEqual(event, actual_events[1])

    def test_multiple_topics(self):
        actual_events = []

        def handler_one(ev):
            actual_events.append(ev)

        def handler_two(ev):
            actual_events.append(ev)

        event_one = Event.for_payload("test payload one - " + self.get_id())
        event_two = Event.for_payload("test payload two - " + self.get_id())

        self.event_bus.subscribe(self.topic + "- One", handler_one)
        self.event_bus.subscribe(self.topic + "- Two", handler_two)
        self.event_bus.publish(self.topic + "- One", event_one)
        self.event_bus.publish(self.topic + "- Two", event_two)

        await_predicate(lambda: len(actual_events) > 1, "event received")

        self.assertEqual(sorted(t for t in self.event_bus.topics), [self.topic + "- One", self.topic + "- Two"])
        self.assertEqual(2, len(actual_events))
        self.assertEqual({event_one.id, event_two.id}, set(e.id for e in actual_events))

    def test_unsubscribe(self):
        actual_events = []

        def handler(ev):
            actual_events.append(ev)

        event = Event.for_payload("test payload - " + self.get_id())

        self.event_bus.subscribe(self.topic, handler)
        self.event_bus.publish(self.topic, event)

        await_predicate(lambda: len(actual_events) > 0, "event received")

        self.event_bus.unsubscribe(self.topic, handler)
        self.event_bus.publish(self.topic, event)

        try:
            await_predicate(lambda: len(actual_events) > 1, "event received", repeat=10)
        except:
            pass

        self.assertEqual(len(actual_events), 1)
        self.assertEqual(actual_events[0], event)


class KombuEventBusContainerTestCase(unittest.TestCase):
    """Test custom serializer functionality in KombuEventBusContainer"""

    def test_custom_serializer_integration(self):
        """Test that custom serializer and deserializer are properly used"""

        def custom_serializer(obj):
            """Custom serializer that adds a test marker"""
            if hasattr(obj, '__dict__'):
                result = dict(obj.__dict__)
                result['_test_serializer_used'] = True
                return result
            else:
                return {'value': obj, '_test_serializer_used': True}

        def custom_deserializer(d):
            """Custom deserializer that creates SimpleNamespace objects"""
            if isinstance(d, dict):
                return SimpleNamespace(**d)
            return d

        class TestEventBusContainer(KombuEventBusContainer):
            def __init__(self):
                # Mock config manager for test
                self._config_manager = mock.create_autospec(ConfigurationManager)
                self._config_manager.get_config.return_value = {
                    "server": "memory:///",
                    "exchange": "test.exchange",
                    "type": "direct",
                    "compression": "bzip2",
                }

            @property
            def config_manager(self):
                return self._config_manager

            @property
            def event_bus_serializer(self):
                return (custom_serializer, custom_deserializer)

        # Test container creation and event bus initialization
        container = TestEventBusContainer()
        event_bus = container.event_bus

        self.assertIsNotNone(event_bus)
        self.assertIsInstance(event_bus, KombuEventBus)

        # Test that we can publish and receive events with custom serialization
        actual_events = []

        def handler(event):
            actual_events.append(event)

        test_payload = SimpleNamespace(name="test_object", value=42)
        test_event = Event.for_payload(test_payload)
        topic = "test.custom.serializer"

        event_bus.subscribe(topic, handler)
        event_bus.publish(topic, test_event)

        # Wait for event to be processed
        await_predicate(lambda: len(actual_events) > 0, "custom serializer event received")

        # Verify event was received
        self.assertEqual(1, len(actual_events))
        received_event = actual_events[0]

        # Verify the payload was properly deserialized
        self.assertIsInstance(received_event.payload, SimpleNamespace)
        self.assertEqual(received_event.payload.name, "test_object")
        self.assertEqual(received_event.payload.value, 42)

        # Verify our custom serializer was used (marker should be present)
        self.assertTrue(hasattr(received_event.payload, '_test_serializer_used'))
        self.assertTrue(received_event.payload._test_serializer_used)

        # Clean up
        event_bus.unsubscribe(topic)


if __name__ == '__main__':
    unittest.main()
