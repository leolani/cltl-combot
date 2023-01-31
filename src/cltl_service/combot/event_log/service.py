import logging
from typing import List

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus, Event
from cltl.combot.infra.event_log import LogWriter

logger = logging.getLogger(__name__)


class EventLogService:
    @classmethod
    def from_config(cls, log_writer: LogWriter, event_bus: EventBus,
                    config_manager: ConfigurationManager):
        if config_manager.has_config("cltl.event_log.event"):
            config = config_manager.get_config("cltl.event_log.event")
            event_topics = config.get("topics", multi=True)
        else:
            # Subscribe to all topics
            event_topics = []

        return cls(event_topics, log_writer, event_bus)

    def __init__(self, input_topics: List[str], log_writer: LogWriter, event_bus: EventBus):
        self._log_writer = log_writer

        self._event_bus = event_bus

        self._input_topics = input_topics
        self._subscribed_topics = None

        self._topic_worker = None
        self._app = None

    def start(self):
        self._log_writer.__enter__()
        self._subscribed_topics = self._input_topics if self._input_topics else self._event_bus.topics
        for topic in self._subscribed_topics:
            self._event_bus.subscribe(topic, self._process)

        logger.info("Subscribed event log to topics %s", self._subscribed_topics)

    def stop(self):
        if self._subscribed_topics is None:
            return

        try:
            for topic in self._subscribed_topics:
                self._event_bus.unsubscribe(topic, self._process)
        finally:
            self._log_writer.__exit__(None, None, None)
            self._subscribed_topics = None

    def _process(self, event: Event):
        self._log_writer.put(event)