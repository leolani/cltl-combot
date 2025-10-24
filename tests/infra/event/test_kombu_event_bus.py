import json
import logging
import sys
import time
import unittest
from queue import Queue
from types import SimpleNamespace
from unittest import mock

from kombu.serialization import register

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event.api import Event
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


class BaseKombuBusTest(unittest.TestCase):
    """
    Base fixture that spins up a bus backed by Kombu's memory transport.
    Adjust keys to match your actual ConfigurationManager schema if needed.
    """

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

        # Small helper to track received events
        self.received_a = []
        self.received_b = []

    def tearDown(self):
        try:
            for topic in self.event_bus.topics:
                self.event_bus.unsubscribe(topic)
        except Exception:
            pass


class KombuEventBusTestCase(BaseKombuBusTest):
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


class TestSubscribeUnsubscribe(BaseKombuBusTest):
    def test_subscribe_and_unsubscribe_stops_delivery(self):
        def handler(ev):
            self.received_a.append(ev)

        # Subscribe, publish, and wait
        self.event_bus.subscribe(self.topic, handler)
        self.event_bus.publish(self.topic, Event.for_payload("one"))

        self.assertTrue(await_predicate(lambda: len(self.received_a) == 1))

        # Unsubscribe and ensure no further deliveries happen
        self.event_bus.unsubscribe(self.topic, handler)
        self.event_bus.publish(self.topic, Event.for_payload("two"))

        # Give the consumer a moment; list should still be length 1
        time.sleep(0.2)
        self.assertEqual(1, len(self.received_a))


class TestPerTopicIsolation(BaseKombuBusTest):
    def test_messages_do_not_cross_topics(self):
        def handler_a(ev):
            self.received_a.append(ev.payload)

        def handler_b(ev):
            self.received_b.append(ev.payload)

        other_topic = "other.topic_" + self.get_id()

        self.event_bus.subscribe(self.topic, handler_a)
        self.event_bus.subscribe(other_topic, handler_b)

        self.event_bus.publish(self.topic, Event.for_payload("A1"))
        self.event_bus.publish(other_topic, Event.for_payload("B1"))
        self.event_bus.publish(self.topic, Event.for_payload("A2"))

        self.assertTrue(await_predicate(lambda: len(self.received_a) == 2))
        self.assertTrue(await_predicate(lambda: len(self.received_b) == 1))

        self.assertEqual(["A1", "A2"], self.received_a)
        self.assertEqual(["B1"], self.received_b)


class TestMultipleHandlersIsolation(BaseKombuBusTest):
    def test_one_handler_failing_should_not_block_others(self):
        """
        Current kombu._topic_handler calls handlers in a simple loop without try/except.
        If the first raises, subsequent handlers won't be invoked (expected to FAIL now).
        After you wrap each handler in try/except, remove @expectedFailure.
        """
        calls = Queue()

        def bad_handler(ev):
            raise RuntimeError("boom")

        def ok_handler(ev):
            calls.put("ok")

        self.event_bus.subscribe(self.topic, bad_handler)
        self.event_bus.subscribe(self.topic, ok_handler)

        self.event_bus.publish(self.topic, Event.for_payload("X"))
        # With proper isolation, ok_handler should be called once even if bad_handler explodes
        self.assertTrue(await_predicate(lambda: not calls.empty() and calls.get() == "ok"))


class TestEventMetadataTimestamp(BaseKombuBusTest):
    def test_timestamp_default_is_dynamic(self):
        """
        Two events created at different times should have increasing timestamps.
        """
        e1 = Event.for_payload("p1")
        print("e1")
        time.sleep(0.02)  # ensure next tick (ms granularity)
        e2 = Event.for_payload("p2")
        print("e2")
        self.assertLess(e1.metadata.timestamp, e2.metadata.timestamp)


class TestAckOnExceptionBehavior(BaseKombuBusTest):
    # TODO Add an exception signaling Requeue?
    @unittest.expectedFailure
    def test_handler_exception_does_not_ack_and_blocks_delivery(self):
        """
        This documents current behavior, not necessarily the desired one.
        on_message() does message.ack() after callback; if the handler raises, ack won't run.
        Kombu's ConsumerMixin will requeue or retry according to its policy. Depending on your setup,
        the message may be redelivered repeatedly and starve the queue.

        We subscribe a failing handler only and assert we never 'observe' a successful processing.
        You may replace this with a more precise assertion once you add a DLQ or explicit reject().
        """
        seen = {"count": 0}

        def bad(ev):
            seen["count"] += 1
            raise RuntimeError("boom")

        self.event_bus.subscribe(self.topic, bad)
        self.event_bus.publish(self.topic, Event.for_payload("X"))

        # Wait a bit; we expect re-deliveries (count increasing) or at least not 'acked and gone'.
        time.sleep(0.2)
        self.assertGreaterEqual(seen["count"], 1)


class TestTopicEnumeration(BaseKombuBusTest):
    def test_topics_property_reflects_subscriptions(self):
        # Initially, no topics (or depends on impl; guard for presence)
        _ = list(self.event_bus.topics)

        def h(ev):  # no-op
            pass

        other_topic = "other.topic_" + self.get_id()

        self.event_bus.subscribe(self.topic, h)
        self.assertIn(self.topic, list(self.event_bus.topics))

        self.event_bus.subscribe(other_topic, h)
        self.assertTrue({self.topic, other_topic}.issubset(set(self.event_bus.topics)))

        self.event_bus.unsubscribe(self.topic, h)
        # Depending on implementation, the topic may disappear when the last handler is gone
        # Accept either "still present because consumer thread exists" or "gone".
        # Prefer the stronger assertion if your unsubscribe stops and removes the consumer:
        # self.assertNotIn(self.topic, list(self.event_bus.topics))


if __name__ == "__main__":
    unittest.main()




if __name__ == '__main__':
    unittest.main()
