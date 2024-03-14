import dataclasses
from dataclasses import dataclass
from typing import List, Any, Tuple


@dataclasses.dataclass()
class Intention:
    label: str
    args: Any


@dataclass
class IntentionEvent:
    intentions: List[Intention]

    def __post_init__(self):
        if not isinstance(self.intentions, (list, tuple)):
            raise ValueError("intentions must be a list")


@dataclass
class DesireEvent:
    achieved: List[str]

    def __post_init__(self):
        if not isinstance(self.achieved, (list, tuple)):
            raise ValueError("achieved must be a list")
