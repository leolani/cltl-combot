import logging

from cltl.combot.backend.api.camera import AbstractCamera
from cltl.combot.backend.api.led import AbstractLed
from cltl.combot.backend.api.microphone import AbstractMicrophone
from cltl.combot.backend.api.motion import AbstractMotion
from cltl.combot.backend.api.tablet import AbstractTablet
from cltl.combot.backend.api.text_to_speech import AbstractTextToSpeech


logger = logging.getLogger(__name__)


class AbstractBackend(object):
    """
    Abstract Backend on which all Backends are based

    Exposes
    :class:`~cltl.combot.backend.api.camera.AbstractCamera`,
    :class:`~cltl.combot.backend.api.microphone.AbstractMicrophone`,
    :class:`~cltl.combot.backend.api.text_to_speech.AbstractTextToSpeech`,
    :class:`~cltl.combot.backend.api.led.AbstractLed` and
    :class:`~cltl.combot.backend.api.tablet.AbstractTablet`.

    Parameters
    ----------
    camera: AbstractCamera
        Backend :class:`~cltl.combot.backend.api.camera.AbstractCamera`
    microphone: AbstractMicrophone
        Backend :class:`~cltl.combot.backend.api.microphone.AbstractMicrophone`
    text_to_speech: AbstractTextToSpeech
        Backend :class:`~cltl.combot.backend.api.text_to_speech.AbstractTextToSpeech`
    led: AbstractLed
        Backend :class:`~cltl.combot.backend.api.led.AbstractLed`
    tablet: AbstractTablet
        Backend :class:`~cltl.combot.backend.api.tablet.AbstractTablet`
    """

    def __init__(self, camera, microphone, text_to_speech, motion, led, tablet):
        # type: (AbstractCamera, AbstractMicrophone, AbstractTextToSpeech, AbstractMotion, AbstractLed, AbstractTablet) -> None
        self._camera = camera
        self._microphone = microphone
        self._text_to_speech = text_to_speech
        self._motion = motion
        self._led = led
        self._tablet = tablet

    def start(self):
        if self._camera:
            self._camera.start()
        if self._microphone:
            self._microphone.start()
        if self._text_to_speech:
            self._text_to_speech.start()

    def stop(self):
        self.stop_safe(self._camera)
        self.stop_safe(self._microphone)
        self.stop_safe(self._text_to_speech)

    def stop_safe(self, component):
        if component:
            try:
                component.stop()
            except:
                logger.exception("Failed to stop " + str(component))

    @property
    def camera(self):
        # type: () -> AbstractCamera
        """
        Reference to :class:`~cltl.combot.backdend.api.camera.AbstractCamera`

        Returns
        -------
        camera: AbstractCamera
        """
        return self._camera

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        """
        Reference to :class:`~cltl.combot.backend.api.microphone.AbstractMicrophone`

        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def text_to_speech(self):
        # type: () -> AbstractTextToSpeech
        """
        Reference to :class:`~cltl.combot.backend.api.text_to_speech.AbstractTextToSpeech`

        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self._text_to_speech

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Reference to :class:`~cltl.combot.backend.api.motion.AbstractMotion`

        Returns
        -------
        motion: AbstractMotion
        """
        return self._motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Reference to :class:`~cltl.combot.backend.api.led.AbstractLed`

        Returns
        -------
        text_to_speech: AbstractLed
        """
        return self._led

    @property
    def tablet(self):
        # type: () -> AbstractTablet
        """
        Reference to :class:`~cltl.combot.backend.api.tablet.AbstractTablet`

        Returns
        -------
        tablet: AbstractTablet
        """
        return self._tablet
