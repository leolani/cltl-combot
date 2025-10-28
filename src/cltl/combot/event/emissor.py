import abc
import uuid
from enum import Enum, auto
from dataclasses import dataclass
from typing import Generic, TypeVar, List, Optional

from emissor.representation.scenario import Modality, AudioSignal, TextSignal, ImageSignal, Signal, Mention, Scenario, \
    ScenarioContext, Annotation

from cltl.combot.infra.time_util import timestamp_now

SIG = TypeVar('SIG', bound=Signal)
MEN = TypeVar('MEN', bound=Mention)


class ConversationalAgent(Enum):
    LEOLANI = auto()
    SPEAKER = auto()


@dataclass
class Agent:
    name: Optional[str] = None
    uri: Optional[str] = None


@dataclass
class LeolaniContext(ScenarioContext):
    agent: Agent
    speaker: Agent
    location_id: str
    location: str
    persons: List[Agent]
    objects: List[str]


@dataclass
class EmissorEvent(abc.ABC):
    type: str


@dataclass
class ScenarioEvent(EmissorEvent):
    scenario: Scenario

    @classmethod
    def create(cls, scenario: Scenario):
        return cls(cls.__name__, scenario)


@dataclass
class ScenarioStarted(ScenarioEvent):
    pass


@dataclass
class ScenarioStopped(ScenarioEvent):
    pass


@dataclass
class SignalEvent(Generic[SIG], EmissorEvent):
    modality: Modality
    signal: SIG


@dataclass
class SignalStarted(Generic[SIG], SignalEvent[SIG]):
    pass


@dataclass
class SignalStopped(Generic[SIG], SignalEvent[SIG]):
    pass


@dataclass
class TextSignalEvent(SignalEvent[TextSignal]):
    @classmethod
    def create(cls, signal: TextSignal):
        return cls(cls.__name__, Modality.TEXT, signal)

    @classmethod
    def for_speaker(cls, signal: TextSignal):
        cls.add_agent_annotation(signal, ConversationalAgent.SPEAKER.name)

        return cls(cls.__name__, Modality.TEXT, signal)

    @classmethod
    def for_agent(cls, signal: TextSignal):
        cls.add_agent_annotation(signal, ConversationalAgent.LEOLANI.name)

        return cls(cls.__name__, Modality.TEXT, signal)

    @staticmethod
    def add_agent_annotation(signal, agent):
        agent_annotation = Annotation(ConversationalAgent.__name__,
                                      agent,
                                      ConversationalAgent.LEOLANI.name,
                                      timestamp_now())
        signal.mentions.append(Mention(str(uuid.uuid4()), [signal.ruler], [agent_annotation]))


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
class AnnotationEvent(Generic[MEN], EmissorEvent):
    mentions: List[MEN]

    @classmethod
    def create(cls, mentions: List[MEN]):
        return cls(cls.__name__, mentions)
