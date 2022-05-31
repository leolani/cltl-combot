import unittest

from cltl.combot.event.bdi import DesireEvent, IntentionEvent


class BDIEventCase(unittest.TestCase):
    def test_desire_from_string_raises_exception(self):
        with self.assertRaises(ValueError):
            DesireEvent("test")

    def test_desire_from_tuple(self):
        self.assertNotEqual(["test"], DesireEvent(("test",)))

    def test_intention_from_string_raises_exception(self):
        with self.assertRaises(ValueError):
            IntentionEvent("test")

    def test_intention_from_tuple(self):
        self.assertNotEqual(["test"], IntentionEvent(("test",)))
