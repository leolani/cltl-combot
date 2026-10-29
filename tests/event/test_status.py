import unittest

from cltl.combot.event.status import StatusEvent


class StatusEventTest(unittest.TestCase):
    def test_defaults(self):
        event = StatusEvent("loading", "asr")

        self.assertEqual("info", event.level)
        self.assertIsNone(event.progress)
        self.assertIsNone(event.ttl)
        self.assertFalse(event.resolved)

    def test_invalid_values_are_rejected(self):
        for kwargs in ({"level": "fatal"}, {"progress": -0.1}, {"progress": 1.1},
                       {"ttl": -1}, {"resolved": True}):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    StatusEvent("m", "s", **kwargs)

    def test_a_persistent_status_cannot_expire_fill_or_end(self):
        self.assertTrue(StatusEvent("m", "s", persistent=True).persistent)
        self.assertFalse(StatusEvent("m", "s").persistent)
        for kwargs in ({"ttl": 1}, {"progress": 0.5}, {"key": "k", "resolved": True}):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    StatusEvent("m", "s", persistent=True, **kwargs)

    def test_a_resolve_needs_a_key(self):
        self.assertTrue(StatusEvent("m", "s", key="k", resolved=True).resolved)
