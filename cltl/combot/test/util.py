from unittest import TestCase

from time import sleep
from typing import Callable, Any

from cltl.combot.infra.config.api import Configuration


class TestConfiguration(Configuration):
    def __init__(self, configuration_dict):
        self._dict = configuration_dict

    def get(self, key, multi=False):
        return self._dict.get(key)

    def get_int(self, key):
        return self.get(key)

    def get_float(self, key):
        return self.get(key)

    def get_boolean(self, key):
        return self.get(key)

    def get_enum(self, key, type, multi=False):
        return self.get(key)


def await_predicate(predicate: Callable[[Any], bool], msg: str = "predicate", repeat: int = 1000,
                    sleep_interval: float = 0.01) -> None:
    cnt = 0
    while not predicate() and cnt < repeat:
        sleep(sleep_interval)
        cnt += 1

    if cnt == repeat:
        raise TestCase.failureException("Test timed out waiting for " + msg)