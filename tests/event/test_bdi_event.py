import unittest

from cltl.combot.event.bdi import DesireEvent, IntentionEvent, Intention


class BDIEventCase(unittest.TestCase):
    def test_desire_from_string_raises_exception(self):
        with self.assertRaises(ValueError):
            DesireEvent("test")

    def test_desire_from_tuple(self):
        self.assertNotEqual(["test"], DesireEvent(("test",)))

    def test_intention_from_string_raises_exception(self):
        with self.assertRaises(ValueError):
            IntentionEvent(Intention("test", None))
