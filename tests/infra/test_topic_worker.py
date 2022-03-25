import logging
import sys
import threading
import time
import unittest

from cltl.combot.event.bdi import IntentionEvent
from cltl.combot.infra.event.api import Event
from cltl.combot.infra.event.memory import SynchronousEventBus
from cltl.combot.infra.topic_worker import TopicWorker, RejectionStrategy


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stderr))


class TestProcessor:
    def __init__(self, start: threading.Event = None):
        self.events = []
        self._start = start
        self.processed = threading.Event()

    def process(self, event):
        if self._start:
            self._start.wait(1)
        self.events.append(event)
        self.processed.set()


class TestTopicWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.event_bus = SynchronousEventBus()
        self.processor = TestProcessor()

    def tearDown(self) -> None:
        self.worker.stop()

    def test_processing(self):
        self.worker = TopicWorker(['testTopic'], self.event_bus, processor=self.processor.process)
        self.worker.start().wait()

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))
        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(1, len(self.processor.events))
        self.assertEqual(1, self.processor.events[0].payload)

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(2))
        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(2, len(self.processor.events))
        self.assertEqual(2, self.processor.events[1].payload)

    def test_processing_with_multiple_topics(self):
        self.worker = TopicWorker(['testTopic', 'testTopicTwo'], self.event_bus, processor=self.processor.process)
        self.worker.start().wait()

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))
        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(1, len(self.processor.events))
        self.assertEqual(1, self.processor.events[0].payload)

        self.processor.processed.clear()
        self.event_bus.publish("testTopicTwo", Event.for_payload(2))
        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(2, len(self.processor.events))
        self.assertEqual(2, self.processor.events[1].payload)

    def test_processing_with_active_intention(self):
        self.worker = TopicWorker(['testTopic'], self.event_bus,
                                  intentions=["testIntention"], intention_topic="intentions",
                                  processor=self.processor.process)
        self.worker.start().wait()

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))

        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(0, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("intentions", Event.for_payload(IntentionEvent(["testIntention"])))
        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(0, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))

        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(1, len(self.processor.events))
        self.assertEqual(1, self.processor.events[0].payload)

        self.processor.processed.clear()
        self.event_bus.publish("intentions", Event.for_payload(IntentionEvent(["otherIntention"])))
        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(1, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))

        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(1, len(self.processor.events))

    def test_processing_with_inactive_intention(self):
        self.worker = TopicWorker(['testTopic'], self.event_bus,
                                  intentions=["!testIntention"], intention_topic="intentions",
                                  processor=self.processor.process)
        self.worker.start().wait()

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))

        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(1, len(self.processor.events))
        self.assertEqual(1, self.processor.events[0].payload)

        self.processor.processed.clear()
        self.event_bus.publish("intentions", Event.for_payload(IntentionEvent(["testIntention"])))
        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(1, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))

        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(1, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("intentions", Event.for_payload(IntentionEvent(["otherIntention"])))
        self.assertFalse(self.processor.processed.wait(0.1))
        self.assertEqual(1, len(self.processor.events))

        self.processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(2))

        self.assertTrue(self.processor.processed.wait(0.01))
        self.assertEqual(2, len(self.processor.events))
        self.assertEqual(2, self.processor.events[1].payload)

    def test_rejection_strategy_drop(self):
        start = threading.Event()
        processor = TestProcessor(start)
        self.worker = TopicWorker(['testTopic'], self.event_bus, processor=processor.process,
                                  rejection_strategy=RejectionStrategy.DROP)
        self.worker.start().wait()

        processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        self.event_bus.publish("testTopic", Event.for_payload(2))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        self.event_bus.publish("testTopic", Event.for_payload(3))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        start.set()

        self.assertTrue(processor.processed.wait(0.01))
        time.sleep(0.1)
        self.assertEqual(2, len(processor.events))
        self.assertEqual([1, 2], [e.payload for e in processor.events])

    def test_rejection_strategy_overwrite(self):
        start = threading.Event()
        processor = TestProcessor(start)
        self.worker = TopicWorker(['testTopic'], self.event_bus, processor=processor.process,
                                  rejection_strategy=RejectionStrategy.OVERWRITE)
        self.worker.start().wait()

        processor.processed.clear()
        self.event_bus.publish("testTopic", Event.for_payload(1))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        self.event_bus.publish("testTopic", Event.for_payload(2))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        self.event_bus.publish("testTopic", Event.for_payload(3))
        self.assertFalse(processor.processed.wait(0.01))
        self.assertEqual(0, len(processor.events))

        start.set()

        self.assertTrue(processor.processed.wait(0.01))
        time.sleep(0.1)
        self.assertEqual(2, len(processor.events))
        self.assertEqual([1, 3], [e.payload for e in processor.events])
