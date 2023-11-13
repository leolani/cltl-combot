import flask
import logging
from flask import Response, request
from typing import List

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus, Event
from cltl.combot.infra.event_log import LogWriter

logger = logging.getLogger(__name__)


class EventBusService:
    @classmethod
    def from_config(cls, event_bus: EventBus, config_manager: ConfigurationManager):
        if config_manager.has_config("cltl.event_bus_endpoint"):
            config = config_manager.get_config("cltl.event_bus_endpoint")
            allowed_topics = config.get("white_list", multi=True)
        else:
            # Only allow white-listed topics
            allowed_topics = []

        return cls(allowed_topics, event_bus)

    def __init__(self, allowed_topics: List[str], event_bus: EventBus):
        self._event_bus = event_bus
        self.allowed_topics = allowed_topics

        self._app = None

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def app(self):
        if self._app:
            return self._app

        self._app = flask.Flask(__name__)

        @self._app.route('/event/<topic>', methods=['POST'])
        def post_event(topic: str):
            if topic not in self.allowed_topics:
                logger.warning("Received event on topic blocked topic %s with payload %s", topic)
                return Response(status=403)

            payload = flask.request.get_data(as_text=True)
            logger.debug("Received event on topic %s with payload %s", topic, payload)
            self._event_bus.publish(topic, Event.for_payload(payload))

            return Response(status=200)

        @self._app.route('/urlmap')
        def url_map():
            return str(self._app.url_map)

        @self._app.after_request
        def set_cache_control(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response

        return self._app
