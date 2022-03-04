from dataclasses import dataclass
from typing import Generic, TypeVar, List

from emissor.representation.scenario import Modality, AudioSignal, TextSignal, ImageSignal, Signal, Mention

S = TypeVar('S', bound=Signal)


@dataclass
class SignalEvent(Generic[S]):
    type: str
    modality: Modality
    signal: S


@dataclass
class SignalStarted(Generic[S], SignalEvent[S]):
    pass


@dataclass
class SignalStopped(Generic[S], SignalEvent[S]):
    pass


@dataclass
class TextSignalEvent(SignalEvent[TextSignal]):
    @classmethod
    def create(cls, signal: TextSignal):
        return cls(cls.__name__, Modality.TEXT, signal)


@dataclass
class ImageSignalEvent(SignalEvent[ImageSignal]):
    @classmethod
    def create(cls, signal: ImageSignal):
        return cls(cls.__name__, Modality.IMAGE, signal)


@dataclass
class AudioSignalStarted(SignalStarted[AudioSignal]):
    @classmethod
    def create(cls, signal: AudioSignal):
        return cls(cls.__name__, Modality.AUDIO, signal)


@dataclass
class AudioSignalStopped(SignalStopped[AudioSignal]):
    @classmethod
    def create(cls, signal: AudioSignal):
        return cls(cls.__name__, Modality.AUDIO, signal)


M = TypeVar('M', bound=Mention)

@dataclass
class AnnotationEvent(Generic[M]):
    type: str
    mentions: List[M]