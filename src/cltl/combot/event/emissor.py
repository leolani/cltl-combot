import abc
from dataclasses import dataclass
from typing import Generic, TypeVar, List

from emissor.representation.scenario import Modality, AudioSignal, TextSignal, ImageSignal, Signal, Mention, Scenario, \
    ScenarioContext

S = TypeVar('S', bound=Signal)
M = TypeVar('M', bound=Mention)


#TODO
@dataclass
class LeolaniContext(ScenarioContext):
    agent: str
    speaker: str
    location_id: str
    location: str


@dataclass
class EmissorEvent(abc.ABC):
    type: str


@dataclass
class ScenarioEvent(EmissorEvent):
    scenario: Scenario


@dataclass
class ScenarioStarted(ScenarioEvent):
    @classmethod
    def create(cls, scenario: Scenario):
        return cls(cls.__name__, scenario)


@dataclass
class ScenarioStopped(ScenarioEvent):
    @classmethod
    def create(cls, scenario: Scenario):
        return cls(cls.__name__, scenario)


@dataclass
class SignalEvent(Generic[S], EmissorEvent):
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


@dataclass
class AnnotationEvent(Generic[M], EmissorEvent):
    mentions: List[M]

    @classmethod
    def create(cls, mentions: List[M]):
        return cls(cls.__name__, mentions)