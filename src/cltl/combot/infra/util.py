import threading

import logging
from threading import Thread
from time import sleep

logger = logging.getLogger(__name__)


class Scheduler(Thread):
    """
    Runs Threaded Task Continuously with certain interval

    This is useful for long running Real-Time tasks:
        When there are many of these tasks, they start to conflict with each other.
        By specifying an interval in which the CPU on this thread is told to sleep,
        breathing room is realized for the other threads to execute their commands.

    Parameters
    ----------
    target: Callable
        Function to Run
    interval: float
        Interval between function calls
    name: str or None
        Name of Thread (for identification in debug mode)
    args: tuple
        Target Arguments
    kwargs: dict
        Target Keyword Arguments
    """

    def __init__(self, target, interval=1E-1, name=None, args=(), kwargs={}):
        Thread.__init__(self, name=name)
        self._target = target
        self._interval = interval
        self._args = args
        self._kwargs = kwargs
        self._running = False

        self.daemon = True

    def run(self):
        self._running = True
        logger.info("Started %s thread", self.name)
        while self._running:
            try:
                self._target(*self._args, **self._kwargs)
            except:
                logger.exception("Error during thread execution (%s)", self.name)
            sleep(self._interval)

    @property
    def running(self):
        return self._running

    def stop(self, timeout=None):
        self._running = False
        logger.info("Stopped %s thread", self.name)


class ThreadsafeBoolean:
    def __init__(self, value: bool = False):
        self._value = value
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, value: bool):
        with self._lock:
            self._value = value

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return str(self.value)