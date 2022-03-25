import logging
import threading
import time
from enum import Enum
from queue import Queue, Empty, Full
from threading import Thread
from typing import Iterable, Optional, Union, Callable

from time import sleep

from cltl.combot.event.bdi import IntentionEvent
from cltl.combot.infra.event.api import EventBus, Event, TopicError
from cltl.combot.infra.resource.api import ResourceManager, LockTimeoutError
from cltl.combot.infra.time_util import timestamp_now
from cltl.combot.infra.util import ThreadsafeBoolean

logger = logging.getLogger(__name__)


_DEPENDENCY_TIMEOUT = 10


class RejectionStrategy(Enum):
    OVERWRITE = 0
    DROP = 1
    BLOCK = 2
    EXCEPTION = 3


class TopicWorker(Thread):
    """
    Process events on a topic from the event bus.

    The topic worker listens to events from the specified topics and puts them
    on an internal processing queue. The queue is then processed in a sequential
    manner.

    The topic worker supports to specify intentions for which it will be accepting or
    rejecting events.

    The topic worker waits until all required resources (typically the topics) are
    available before starting to listen to the specified topics. It also registers
    the specified provided resources before starting.

    For the case when a maximum size for the processing queue is specified and
    events are received faster than they can be processed, a rejection strategy
    can be provided.
    """

    def __init__(self, topics: Union[str, Iterable[str]], event_bus: EventBus,
                 interval: float = 0, scheduled: float = None, name: str = None, buffer_size: int = 1,
                 rejection_strategy: RejectionStrategy = RejectionStrategy.OVERWRITE,
                 resource_manager: ResourceManager = None,
                 requires: Iterable[str] = (), provides: Iterable[str] = (),
                 intentions: Iterable[str] = (), intention_topic: str = None,
                 processor: Callable[[Optional[Event]], None] = None):
        """
        Parameters
        ----------
        topics : Union[str, Iterable[str]]
            One or more topics the worker is listening to.
        event_bus : EventBus
            The Event bus of the application.
        interval : float
            Wait interval between processing consecutive events.
        scheduled : float
            If set, the processor is invoked after the specified amount of
            seconds even if there is no event scheduled.
        name : str
            Name of the topic worker.
        buffer_size : int
            Size of the internal buffer of the worker.
        rejection_strategy : RejectionStrategy
            Strategy to use when the interal buffer is full.
        resource_manager : ResourceManager
            The resource manager of the application.
        requires : Iterable[str]
            Resources required by the topic worker.
        provides : Iterable[str]
            Resources provided by the topic worker.
        intentions : Iterable[str]
            Intention identifiers for which the `TopicWorker` will be active. If the
            identifier is prefixed with and `!` the `TopicWorker` will be inactive
            for the respective intention.
        intention_topic : str
            The topic name on which the `TopicWorker` will listen to `IntentionEvent`s
        processor :  Callable[[Optional[Event]], None]
            Function to call for each event. Alternatively override the `process` method.
        """
        super(TopicWorker, self).__init__(name=name if name else self.__class__.__name__)
        self._event_bus = event_bus
        self._topics = set(topics) if not isinstance(topics, str) else {topics}
        self._interval = interval
        self._scheduled = scheduled
        self._buffer = Queue(maxsize=buffer_size)
        self._strategy = rejection_strategy
        self._resource_manager = resource_manager
        self._requires = requires
        self._provides = provides

        self._intention_topic = intention_topic
        self._inactive_intentions = set(intention[1:] for intention in intentions if intention.startswith("!"))
        self._active_intentions = set(intention for intention in intentions if not intention.startswith("!"))
        self._intention_lock = threading.Lock()
        self._active = ThreadsafeBoolean(not self._active_intentions)

        self._started = threading.Event()
        self._running = False
        self._stop_event = None

        self._processor = processor

    def start(self):
        logger.info("Starting topic worker %s", self.name)

        super(TopicWorker, self).start()

        return self._started

    def stop(self):
        for topic in self._topics:
            try:
                self._event_bus.unsubscribe(topic, self.__accept_event)
            except:
                logger.exception("Failed to unsubscribe " + self.name + " from " + topic)

        self._running = False
        self._stop_event = threading.Event()
        logger.info("Stopping topic worker %s", self.name)

    def await_stop(self):
        if not self._stop_event:
            raise ValueError("Worker " + self.name + " is not stopped")

        self._stop_event.wait(_DEPENDENCY_TIMEOUT)

    def run(self):
        self.__resolve_dependencies()
        self._running = True

        for topic in self._topics:
            self._event_bus.subscribe(topic, self.__accept_event)
        if self._intention_topic:
            self._event_bus.subscribe(self._intention_topic, self.__accept_event)

        self._started.set()

        logger.info("Started topic worker %s", self.name)

        while self._running:
            self.__process_event()
            if self._interval:
                sleep(self._interval)

        if self._stop_event:
            self._stop_event.set()
        logger.info("Stopped topic worker %s", self.name)

    def __process_event(self):
        try:
            start = timestamp_now()
            block = self._interval == 0
            timeout = self._scheduled if self._scheduled else 1  # Never block forever
            event = self._buffer.get(block=block, timeout=timeout)
            self.process(event)
            logger.debug("Processed event %s in %s ms for %s", event.id, timestamp_now() - start, self.name)
        except Empty:
            if self._scheduled:
                self.process(None)
        except:
            logger.exception("Error during thread execution (%s)", self.name)

    def __accept_event(self, event):
        accept = self._check_intention(event)
        if not accept:
            return

        handled = False
        while not handled:
            try:
                self._buffer.put(event, block=self._strategy == RejectionStrategy.BLOCK)
                handled = True
                logger.debug("Queued event %s for %s", event.id, self.name)
            except Full as e:
                if self._strategy == RejectionStrategy.EXCEPTION:
                    raise e

                if self._strategy == RejectionStrategy.OVERWRITE:
                    try:
                        dropped = self._buffer.get(block=False)
                        logger.debug("Overwrote event %s with %s for %s", dropped.id, event.id, self.name)
                    except Empty:
                        pass
                elif self._strategy == RejectionStrategy.DROP:
                    handled = True
                    logger.debug("Dropped event %s for %s", event.id, self.name)
                else:
                    raise ValueError("Unknown strategy: " + str(self._strategy))

    def _check_intention(self, event: Event[IntentionEvent]) -> bool:
        if not self._active_intentions and not self._inactive_intentions:
            return True

        if event.metadata.topic != self._intention_topic:
            return self._active.value

        if hasattr(event.payload, 'intentions'):
            intentions = set(event.payload.intentions)
            with self._intention_lock:
                if intentions & self._inactive_intentions:
                    self._active.value = False
                elif not self._active_intentions:
                    self._active.value = True
                else:
                    self._active.value = bool(intentions & self._active_intentions)

            logger.info("%s topic worker %s for intentions %s", "Activated" if self._active else "Deactivated",
                        self.name, intentions)

        return self._intention_topic in self._topics

    def __resolve_dependencies(self):
        if self._resource_manager:
            for required in self._requires:
                try:
                    self._resource_manager.get_read_lock(required, timeout=_DEPENDENCY_TIMEOUT)
                except LockTimeoutError as e:
                    raise TopicError(self.name + " failed to obtain required topic: " + required)

            for provided in self._provides:
                try:
                    self._resource_manager.provide_resource(provided)
                except ValueError:
                    # Ignore error if resource is already provided
                    pass

    def process(self, event: Optional[Event]) -> None:
        """
        Process incoming events.

        Override this method or provide a processing function to the constructor.

        Parameters
        ----------
        event : Optional[Event]
            The next event or None if no event was available and the topcic worker is configured
            to be called in a scheduled manner.
        """
        if self._processor:
            self._processor(event)

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus
