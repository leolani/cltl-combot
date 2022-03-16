from dataclasses import dataclass
from typing import List


@dataclass
class IntentionEvent:
    intentions: List[str]


@dataclass
class DesireEvent:
    achieved: List[str]