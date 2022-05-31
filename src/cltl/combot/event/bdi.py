from dataclasses import dataclass
from typing import List


@dataclass
class IntentionEvent:
    intentions: List[str]

    def __post_init__(self):
        if not isinstance(self.intentions, (list, tuple)):
            raise ValueError("intentions must be a list")


@dataclass
class DesireEvent:
    achieved: List[str]

    def __post_init__(self):
        if not isinstance(self.achieved, (list, tuple)):
            raise ValueError("achieved must be a list")
