from collections import defaultdict
from typing import DefaultDict, Optional

DEFAULT_MAX_LISTENERS = 10


class EventEmitter:
    def __init__(self, max_listeners: Optional[int] = None) -> None:
        self._events: DefaultDict[str, list] = defaultdict(list)
        self.set_max_listeners(max_listeners or DEFAULT_MAX_LISTENERS)

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, key) -> list:
        if key not in self._events:
            raise KeyError(key)

        return self._events.get(key)

    def __delitem__(self, key) -> None:
        del self._events[key]

    def __contains__(self, key) -> bool:
        return key in self._events

    @property
    def max_listeners(self) -> int:
        return self._max_listeners

    def set_max_listeners(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"set_max_listeners() argument must be a integer, not '{type(value)}'")

        if value < 0:
            raise TypeError('set_max_listeners() argument must be a non-negative integer')

        self._max_listeners = value
