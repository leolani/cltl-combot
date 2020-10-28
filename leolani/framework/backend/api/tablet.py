import logging

from typing import Union

from leolani.framework.infra.event.api import EventBus
from leolani.framework.infra.resource.api import ResourceManager

logger = logging.getLogger(__name__)


TOPIC = "leolani.framework.backend.api.tablet.topic"


class AbstractTablet(object):
    """Access Robot Tablet to show URLs"""

    def __init__(self, event_bus, resource_manager):
        # type: (EventBus, ResourceManager) -> None
        self._log = logger.getChild(self.__class__.__name__)

        event_bus.subscribe(TOPIC, self._event_handler)
        resource_manager.provide_resource(TOPIC)

    def _event_handler(self, event):
        payload = event.payload
        url = payload['url']

        if url:
            self.show(url)
        else:
            self.hide()

    def show(self, url):
        # type: (Union[str, unicode]) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        raise NotImplementedError()

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        raise NotImplementedError()
