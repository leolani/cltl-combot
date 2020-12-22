import kombu
from kombu import connections
from time import time

import sys
from unittest import mock

import unittest

from cltl.combot.test.util import await_predicate
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event.api import Event, EventMetadata
from cltl.combot.infra.event.kombu import KombuEventBus


import logging

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class KombuEventBusTestCase(unittest.TestCase):

    counter = 0

    def get_id(self):
        KombuEventBusTestCase.counter += 1
        return str(KombuEventBusTestCase.counter)

    def setUp(self):
        config_manager = mock.create_autospec(ConfigurationManager)
        config_manager.get_config.return_value = {"server": "memory:///"}
        self.event_bus = KombuEventBus(config_manager)
        self.topic = "test topic - " + self.get_id()

    def tearDown(self) -> None:
        for topic in self.event_bus.topics:
            self.event_bus.unsubscribe(topic)

    def test_publish(self):
        event = Event("test payload - " + self.get_id(), EventMetadata())
        self.event_bus.publish(self.topic, event)

        self.assertEqual([self.topic], [ t for t in self.event_bus.topics ])

    def test_subscribe(self):
        actual_events = []

        def handler(ev):
            actual_events.append(ev)

        event = Event("test payload - " + self.get_id(), EventMetadata())

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

        event = Event("test payload - " + self.get_id(), EventMetadata())

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

        event_one = Event("test payload one - " + self.get_id(), EventMetadata())
        event_two = Event("test payload two - " + self.get_id(), EventMetadata())

        self.event_bus.subscribe(self.topic + "- One", handler_one)
        self.event_bus.subscribe(self.topic + "- Two", handler_two)
        self.event_bus.publish(self.topic + "- One", event_one)
        self.event_bus.publish(self.topic + "- Two", event_two)

        await_predicate(lambda: len(actual_events) > 1, "event received")

        self.assertEqual(sorted(t for t in self.event_bus.topics), [self.topic + "- One", self.topic + "- Two"])
        self.assertEqual(2, len(actual_events))
        self.assertEqual(event_one, actual_events[0])
        self.assertEqual(event_two, actual_events[1])

    def test_unsubscribe(self):
        actual_events = []

        def handler(ev):
            actual_events.append(ev)

        event = Event("test payload - " + self.get_id(), EventMetadata())

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


if __name__ == '__main__':
    unittest.main()
