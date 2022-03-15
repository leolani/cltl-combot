import abc
import logging
from collections import OrderedDict

from cltl.combot.infra.event import Event
from cltl.combot.infra.time_util import timestamp_now
from cltl.combot.infra.topic_worker import RejectionStrategy
from typing import Callable, List

logger = logging.getLogger(__name__)


class _OrderedSet(OrderedDict):
    def add(self, elem):
        self[elem] = None


class Group(abc.ABC):
    """
    Group of events for a key.
    """
    def __init__(self):
        self._timestamp = timestamp_now()

    @property
    def timestamp(self) -> int:
        """
        Returns
        -------
        int
            The creation timestamp of the group in milliseconds.
        """
        return self._timestamp

    @property
    def key(self) -> str:
        """
        Returns
        -------
        str
            The key associated with the `Group`.
        """
        raise NotImplementedError()

    @property
    def complete(self) -> bool:
        """
        Determine whether the group is considered complete, i.e. all events required to process the group were received.

        Returns
        -------
        bool
            True if the `Group` is complete, False otherwise.
        """
        raise NotImplementedError()

    def add(self, event: Event):
        """
        Add the given event to the group.

        Parameters
        ----------
        event : Event
            The event.
        """
        raise NotImplementedError()


class GroupProcessor(abc.ABC):
    """
    Processor to handle grouped events.
    """

    def get_key(self, event: Event):
        """
        Get the group key for an event. Events will be grouped by this key.

        Parameters
        ----------
        event : Event
            The event.

        Returns
        -------
        str
            The key associated with the event.
        """
        raise NotImplementedError()

    def new_group(self, key: str) -> Group:
        """
        Create a new `Group` instance for the given key.

        Parameters
        ----------
        key :
            The key associated with the `Group`.

        Returns
        -------
        Group:
            A new `Group` instance for the key.
        """
        raise NotImplementedError()

    def process_group(self, group: Group):
        """
        Process the provided `Group`.

        Parameters
        ----------
        group : Group
            The group to be processed.
        """
        raise NotImplementedError()


class GroupByProcessor:
    """
    Utility class to collect events grouped by a key and process the grouped events once collection is finished.

    To use the `GroupByProcessor` implement the `Group` interface to collect events for a given key, and the
    `GroupProcessor` interface to process a group once all necessary events are collected.

    The `GroupByProcessor` can be configured to hold a maximum size of groups at a time, with different rejection
    strategies once the limit is reached. Additionally, it can be configured to drop incomplete groups after a given
    timeout is reached.
    """
    def __init__(self, group_processor: GroupProcessor,
                 max_size: int = 1, rejection_strategy: RejectionStrategy = RejectionStrategy.DROP,
                 buffer_size: int = None, timeout: int = None):
        """
        Create a new instance of the `GroupByProcessor`.

        Parameters
        ----------
        group_processor : GroupProcessor
            The GroupProcessor to be used.
        max_size : int
            The maximum number of groups to hold at a time, defaults to 1. If the maximum is reached, the configured
            `rejection_strategy` is applied.
        rejection_strategy : RejectionStrategy
            The strategy to apply once the maximum size of groups is reached, defaults to RejectionStrategy.DROP:
                - RejectionStrategy.DROP will ignore all subsequent events for new group keys that were seen while the
                  `GroupByProcessor` reached the maximum number of groups.
                - RejectionStrategy.OVERWRITE will drop the oldest incomplete group when an event for an unknown group
                  keys is received while the `GroupByProcessor` reached the maximum number of groups and accept the
                  event for the new key. Subsequent events for the dropped group will be ignored.
                - RejectionStrategy.EXCEPTION will raise an exception when an event for an unknown group
                  keys is received while the `GroupByProcessor` reached the maximum number of groups.
                - RejectionStrategy.BLOCK is not supported.
        buffer_size : int
            The size of buffers used to remember group keys for dropped and completed groups, defaults to ten times the
            maximum size, but at least 1024. When set to zero, events for completed or dropped keys will not be ignored.
        timeout :
            The timeout after which an incomplete group will be dropped, defaults to None.
        """
        if rejection_strategy == RejectionStrategy.BLOCK:
            raise ValueError("Unsupported rejection strategy: " + RejectionStrategy.BLOCK.name)

        self._group_processor = group_processor
        self._groups = OrderedDict()
        self._completed = _OrderedSet()
        self._dropped = _OrderedSet()
        self._max_size = max_size
        self._rejection_strategy = rejection_strategy
        self._buffer_size = buffer_size if buffer_size is not None else max(10 * max_size, 1024)
        self._timeout = timeout

    def __getitem__(self, item):
        return self._groups[item]

    def __len__(self):
        return len(self._groups)

    def process(self, event: Event):
        """
        Submit an event to the `GroupByProcessor`.

        Parameters
        ----------
        event : Event
            The event.
        """
        self._drop_expired_groups()

        key = self._get_key(event)
        if key is None:
            return

        if key not in self._groups:
            self._groups[key] = self._group_processor.new_group(key)

        self._groups[key].add(event)

        if self._groups[key].complete:
            self._group_processor.process_group(self._groups[key])
            self._completed.add(key)
            del self._groups[key]

        self._truncate_buffers()

    def _drop_expired_groups(self):
        if not self._timeout:
            return

        current = timestamp_now()
        expired = [key for key, group in self._groups.items() if current - group.timestamp > self._timeout]
        for key in expired:
            logger.debug("Group %s timed out", key)
            self._groups.popitem(last=False)

    def _get_key(self, event: Event):
        key = self._group_processor.get_key(event)

        if key in self._completed:
            logger.exception("Received event for completed group %s: %s", key, event)
            key = None
        elif key in self._dropped:
            key = None
        elif len(self._groups) == self._max_size and key not in self._groups:
            if self._rejection_strategy == RejectionStrategy.DROP:
                self._dropped.add(key)
                key = None
            elif self._rejection_strategy == RejectionStrategy.OVERWRITE:
                dropped_key, _ = self._groups.popitem(last=False)
                self._dropped.add(dropped_key)
            elif self._rejection_strategy == RejectionStrategy.EXCEPTION:
                raise ValueError(f"Max size reached: {self._max_size}")

        return key

    def _truncate_buffers(self):
        if len(self._completed) > self._buffer_size:
            self._completed.popitem(last=False)
        if len(self._dropped) > self._buffer_size:
            self._dropped.popitem(last=False)


class SizeGroup(Group):
    def __init__(self, key, size):
        super().__init__()
        self._key = key
        self._size = size
        self.events = []

    @property
    def key(self):
        return self._key

    @property
    def complete(self):
        return len(self.events) == self._size

    def add(self, event: Event):
        self.events.append(event)


class SizeGroupProcessor(GroupProcessor):
    def __init__(self, size,
                 key: Callable[[Event], str],
                 processor: Callable[[List[Event]], None]):
        self._key = key
        self._processor = processor
        self._size = size

    def get_key(self, event: Event) -> str:
        return self._key(event)

    def new_group(self, key: str) -> SizeGroup:
        return SizeGroup(key, self._size)

    def process_group(self, group: SizeGroup):
        self._processor(group.events)

