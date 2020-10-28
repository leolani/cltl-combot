import logging

from leolani.framework.application.component import AbstractComponent
from leolani.framework.backend.api.led import AbstractLed
from leolani.framework.backend.api.motion import AbstractMotion
from leolani.framework.backend.api.tablet import AbstractTablet
from leolani.framework.backend.container import BackendContainer

logger = logging.getLogger(__name__)


class AbstractIntention(AbstractComponent, BackendContainer):
    """
    The Intention class is at the base of more involved robot applications.
    They allow for switching between robot behaviours.
    """

    def __init__(self):
        # type: () -> None
        super(AbstractIntention, self).__init__()

        self._on_change = None

        # Update User of Intention Switch
        self._log = logger.getChild(self.__class__.__name__)

    def start(self):
        super(AbstractIntention, self).start()
        self.log.info("Started Intention")

    def stop(self):
        super(AbstractIntention, self).stop()
        self.log.info("Stopped Intention")

    @property
    def on_intention_change(self):
        return self._on_change

    @on_intention_change.setter
    def on_intention_change(self, handler):
        self._on_change = handler

    @property
    def log(self):
        """
        Intention `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    def change_intention(self, new_intention):
        if self._on_change:
            self._on_change(new_intention)

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Returns :class:`~leolani.framework.backend.api.motion.AbstractMotion` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Returns :class:`~leolani.framework.backend.api.led.AbstractLed` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.led

    @property
    def tablet(self):
        # type: () -> AbstractTablet
        """
        Returns :class:`~leolani.framework.backend.api.tablet.AbstractTablet` associated with current Backend

        Returns
        -------
        tablet: AbstractTablet
        """
        return self.backend.tablet
