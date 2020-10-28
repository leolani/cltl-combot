import logging
from logging import Logger

logger = logging.getLogger(__name__)


class AbstractComponent():
    def __init__(self):
        # type: () -> None
        super(AbstractComponent, self).__init__()

        self._log = logger.getChild(self.__class__.__name__)
        self._log.info("Initializing")

    def start(self):
        pass

    def stop(self):
        super(AbstractComponent, self).stop()

    @property
    def log(self):
        # type: () -> Logger
        """
        Returns Component `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        logger: logging.Logger
        """
        return self._log