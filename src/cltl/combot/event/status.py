from dataclasses import dataclass
from typing import Optional

LEVELS = ("info", "warning", "error")


@dataclass
class StatusEvent:
    """What a module is doing, for a person to read.

    `key` names a status so that it can be replaced or ended: an event with
    `resolved=True` ends the status with the same key. Events without a key are
    fire-and-forget and rely on `ttl` (seconds) to go away.

    A `persistent` status is not a status bar entry but a line in the chat
    history, which stays. It has nothing to expire, fill or end, so it cannot
    carry `ttl`, `progress` or `resolved`.
    """
    message: str
    source: str
    level: str = "info"
    progress: Optional[float] = None
    ttl: Optional[float] = None
    key: Optional[str] = None
    resolved: bool = False
    persistent: bool = False

    def __post_init__(self):
        if self.level not in LEVELS:
            raise ValueError("level must be one of " + ", ".join(LEVELS) + ": " + str(self.level))
        if self.progress is not None and not 0 <= self.progress <= 1:
            raise ValueError("progress must be between 0 and 1: " + str(self.progress))
        if self.ttl is not None and self.ttl < 0:
            raise ValueError("ttl must not be negative: " + str(self.ttl))
        if self.resolved and not self.key:
            raise ValueError("a resolved status needs a key")
        if self.persistent and (self.resolved or self.ttl is not None or self.progress is not None):
            raise ValueError("a persistent status cannot have a ttl, a progress or be resolved")
