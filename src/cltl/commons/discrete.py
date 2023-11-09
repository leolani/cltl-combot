from enum import Enum, auto


class Certainty(Enum):
    UNDERSPECIFIED = 0
    POSSIBLE = 1
    PROBABLE = 2
    CERTAIN = 3

    @staticmethod
    def from_str(label):
        try:
            return Certainty[label.upper()]
        except:
            return Certainty.UNDERSPECIFIED

    @staticmethod
    def from_float(numeric):
        if numeric > .90:
            return Certainty.CERTAIN
        elif numeric >= .50:
            return Certainty.PROBABLE
        elif numeric > 0:
            return Certainty.POSSIBLE
        else:
            return Certainty.UNDERSPECIFIED

    @staticmethod
    def as_enum(value):
        # Convert to enum
        if value is None:
            return Certainty.UNDERSPECIFIED
        elif isinstance(value, Certainty):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return Certainty.from_float(value)
        elif isinstance(value, str) and value.isnumeric():
            return Certainty.from_float(float(value))
        elif isinstance(value, str):
            return Certainty.from_str(value)
        else:
            return Certainty.UNDERSPECIFIED


class Polarity(Enum):
    UNDERSPECIFIED = 0
    NEGATIVE = -1
    POSITIVE = 1

    @staticmethod
    def from_str(label):
        try:
            return Polarity[label.upper()]
        except:
            return Polarity.UNDERSPECIFIED

    @staticmethod
    def from_float(numeric):
        if numeric >= 0:
            return Polarity.POSITIVE
        elif numeric < 0:
            return Polarity.NEGATIVE

    @staticmethod
    def as_enum(value):
        # Convert to enum
        if value is None:
            return Polarity.UNDERSPECIFIED
        elif isinstance(value, Polarity):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return Polarity.from_float(value)
        elif isinstance(value, str) and value.isnumeric():
            return Polarity.from_float(float(value))
        elif isinstance(value, str):
            return Polarity.from_str(value)
        else:
            return Polarity.UNDERSPECIFIED


class Sentiment(Enum):
    UNDERSPECIFIED = 0
    NEGATIVE = -1
    POSITIVE = 1
    NEUTRAL = 0
    EXTREME_NEG = -2
    EXTREME_POS = 2

    @staticmethod
    def from_str(label):
        try:
            return Sentiment[label.upper()]
        except:
            return Sentiment.UNDERSPECIFIED

    @staticmethod
    def from_float(numeric):
        if numeric > 0:
            return Sentiment.POSITIVE
        elif numeric < 0:
            return Sentiment.NEGATIVE
        elif numeric == 0:
            return Sentiment.NEUTRAL

    @staticmethod
    def as_enum(value):
        # Convert to enum
        if value is None:
            return Sentiment.UNDERSPECIFIED
        elif isinstance(value, Sentiment):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return Sentiment.from_float(value)
        elif isinstance(value, str) and value.isnumeric():
            return Sentiment.from_float(float(value))
        elif isinstance(value, str):
            return Sentiment.from_str(value)
        else:
            return Sentiment.UNDERSPECIFIED


class Emotion(Enum):
    UNDERSPECIFIED = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    JOY = 4
    SADNESS = 5
    SURPRISE = 6
    NEUTRAL = 7

    @staticmethod
    def from_str(label):
        try:
            return Emotion[label.upper()]
        except:
            return Emotion.UNDERSPECIFIED

    @staticmethod
    def as_enum(value):
        # Convert to enum
        if value is None:
            return Emotion.UNDERSPECIFIED
        elif isinstance(value, Emotion):
            return value
        # elif isinstance(value, int) or isinstance(value, float):
        #     return Emotion.from_float(value)
        # elif isinstance(value, str) and value.isnumeric():
        #     return Emotion.from_float(float(value))
        elif isinstance(value, str):
            if value.startswith("EmotionType.GO"):
                return GoEmotion[value.split(':')[-1].upper()]
            if value.startswith("EmotionType.EKMAN"):
                return Emotion[value.split(':')[-1].upper()]
            elif value.startswith("EmotionType.SENTIMENT"):
                return Sentiment[value.split(':')[-1].upper()]

            return Emotion.from_str(value)
        else:
            return Emotion.UNDERSPECIFIED


class GoEmotion(Enum):
    AMUSEMENT = auto()
    EXCITEMENT = auto()
    JOY = auto()
    LOVE = auto()
    DESIRE = auto()
    OPTIMISM = auto()
    CARING = auto()
    PRIDE = auto()
    ADMIRATION = auto()
    GRATITUDE = auto()
    RELIEF = auto()
    APPROVAL = auto()
    FEAR = auto()
    NERVOUSNESS = auto()
    REMORSE = auto()
    EMBARRASSMENT = auto()
    DISAPPOINTMENT = auto()
    SADNESS = auto()
    GRIEF = auto()
    DISGUST = auto()
    ANGER = auto()
    ANNOYANCE = auto()
    DISAPPROVAL = auto()
    REALIZATION = auto()
    SURPRISE = auto()
    CURIOSITY = auto()
    CONFUSION = auto()
    NEUTRAL = auto()


class Time(Enum):
    UNDERSPECIFIED = 0
    PAST = 1
    PRESENT = 2
    FUTURE = 3


class UtteranceType(str, Enum):
    STATEMENT = auto()
    QUESTION = auto()
    EXPERIENCE = auto()
    TEXT_MENTION = auto()
    IMAGE_MENTION = auto()
    TEXT_ATTRIBUTION = auto()
    IMAGE_ATTRIBUTION = auto()
