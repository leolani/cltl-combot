import unittest

from cltl.combot.infra.event import Event
from cltl.combot.infra.groupby_processor import SizeGroupProcessor, GroupByProcessor
from cltl.combot.infra.topic_worker import RejectionStrategy


def _event(label):
    return Event.for_payload(label)


def _payloads(events):
    return [e.payload for e in events]


def _head(event):
    return event.payload[0]


def _append(group):
    return lambda events: group.extend(_payloads(events))


class TestGroupBy(unittest.TestCase):
    def test_grouping(self):
        processed = []
        grouping = SizeGroupProcessor(3, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=10)

        self.assertEqual("1", grouping.get_key(_event("10")))
        self.assertEqual("2", grouping.get_key(_event("20")))

        groupby.process(_event("10"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["10"], _payloads(groupby["1"].events))

        groupby.process(_event("11"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["10", "11"], _payloads(groupby["1"].events))

        groupby.process(_event("20"))
        self.assertEqual(2, len(groupby))
        self.assertEqual(["10", "11"], _payloads(groupby["1"].events))
        self.assertEqual(["20"], _payloads(groupby["2"].events))

    def test_not_processed_if_not_complete(self):
        processed = []
        grouping = SizeGroupProcessor(3, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=10)

        groupby.process(_event("10"))
        groupby.process(_event("20"))
        groupby.process(_event("11"))
        groupby.process(_event("21"))
        self.assertEqual([], processed)

    def test_processed_when_complete(self):
        processed = []
        grouping = SizeGroupProcessor(3, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=10)

        groupby.process(_event("10"))
        groupby.process(_event("20"))
        groupby.process(_event("11"))
        groupby.process(_event("21"))
        self.assertEqual([], processed)

        groupby.process(_event("12"))
        self.assertEqual(["10", "11", "12"], processed)
        groupby.process(_event("22"))
        self.assertEqual(["10", "11", "12", "20", "21", "22"], processed)

    def test_events_for_dropped_groups(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=1)

        groupby.process(_event("10"))
        self.assertEqual(1, len(groupby))

        groupby.process(_event("20"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["10"], _payloads(groupby["1"].events))

        groupby.process(_event("11"))
        self.assertEqual(["10", "11"], processed)
        self.assertEqual(0, len(groupby))

        groupby.process(_event("21"))
        self.assertEqual(0, len(groupby))
        self.assertEqual(["10", "11"], processed)

    def test_events_for_completeed_groups(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=1)

        groupby.process(_event("10"))
        self.assertEqual(1, len(groupby))
        groupby.process(_event("11"))
        self.assertEqual(["10", "11"], processed)
        self.assertEqual(0, len(groupby))

        groupby.process(_event("13"))
        self.assertEqual(0, len(groupby))
        self.assertEqual(["10", "11"], processed)

    def test_rejection_drop_drops_event(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=1)

        groupby.process(_event("10"))
        self.assertEqual(1, len(groupby))

        groupby.process(_event("20"))
        self.assertEqual(1, len(groupby))
        groupby.process(_event("30"))
        self.assertEqual(1, len(groupby))

        self.assertEqual(["10"], _payloads(groupby["1"].events))

        groupby.process(_event("11"))
        self.assertEqual(["10", "11"], processed)
        self.assertEqual(0, len(groupby))

        groupby.process(_event("40"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["40"], _payloads(groupby["4"].events))

    def test_rejection_overwrite_replaces_group(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=1, rejection_strategy=RejectionStrategy.OVERWRITE)

        groupby.process(_event("10"))
        self.assertEqual(1, len(groupby))

        groupby.process(_event("20"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["20"], _payloads(groupby["2"].events))
        groupby.process(_event("30"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["30"], _payloads(groupby["3"].events))

        groupby.process(_event("31"))
        self.assertEqual(["30", "31"], processed)
        self.assertEqual(0, len(groupby))

        groupby.process(_event("40"))
        self.assertEqual(1, len(groupby))
        self.assertEqual(["40"], _payloads(groupby["4"].events))

    def test_rejection_exception_raises_excption(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))
        groupby = GroupByProcessor(grouping, max_size=1, rejection_strategy=RejectionStrategy.EXCEPTION)

        groupby.process(_event("10"))

        with self.assertRaises(ValueError):
            groupby.process(_event("20"))

    def test_rejection_block_not_supported(self):
        processed = []
        grouping = SizeGroupProcessor(2, key=_head, processor=_append(processed))

        with self.assertRaises(ValueError):
            GroupByProcessor(grouping, max_size=1, rejection_strategy=RejectionStrategy.BLOCK)
