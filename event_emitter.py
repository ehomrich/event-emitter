from warnings import warn
from collections import defaultdict
from functools import wraps
from typing import DefaultDict, Optional, Tuple, Union, List, Callable, Any

DEFAULT_MAX_LISTENERS = 10


class MaxListenersExceededWarning(UserWarning):
    pass


def _warn_possible_memory_leak(event: str, count: int) -> None:
    warn(
        'Possible EventEmitter memory leak detected. '
        f"{count} '{event}' listeners added. "
        'Use emitter.set_max_listeners() to increase limit.',
        MaxListenersExceededWarning
    )


class EventEmitter:
    def __init__(self, max_listeners: Optional[int] = None) -> None:
        self._events: DefaultDict[str, list] = defaultdict(list)
        self.set_max_listeners(max_listeners if max_listeners is not None else DEFAULT_MAX_LISTENERS)

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, key: str) -> list:
        if key not in self._events:
            raise KeyError(key)

        return self._events.get(key)

    def __delitem__(self, key: str) -> None:
        del self._events[key]

    def __contains__(self, key: str) -> bool:
        return key in self._events

    @property
    def max_listeners(self) -> int:
        return self._max_listeners

    def set_max_listeners(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(
                f"set_max_listeners() argument must be a non-negative "
                f"integer, not '{type(value)}'"
            )

        if value < 0:
            raise ValueError(
                'set_max_listeners() argument must be a non-negative integer'
            )

        self._max_listeners = value

    def event_names(self) -> Tuple[str]:
        return tuple(key for key, val in self._events.items() if len(val) > 0)

    def _get_listeners(self, event: str) -> Union[List[Callable], Tuple]:
        return self._events.get(event, ())

    def listeners(self, event: str) -> Tuple[Callable]:
        return tuple(self._get_listeners(event))

    def count(self, event: str) -> int:
        return len(self._get_listeners(event))

    def full(self, event: str) -> bool:
        return self.count(event) >= self.max_listeners

    def _add_listener(self, event: str, handler: Callable, *, prepend: bool = False) -> None:
        if prepend:
            self._events[event].insert(0, handler)
        else:
            self._events[event].append(handler)

        self.emit('new_listener', event, handler)

        if self.full(event):
            _warn_possible_memory_leak(event, self.count(event))

    def add_listener(self, event: str, handler: Callable) -> None:
        self._add_listener(event, handler, prepend=False)

    def on(self, event: str, handler: Optional[Callable] = None) -> Callable:
        def wrapper(fn: Callable) -> Callable:
            self.add_listener(event, fn)
            return fn

        if handler is not None:
            return wrapper(handler)

        return wrapper

    def preprend_listener(self, event: str, handler: Callable) -> None:
        self._add_listener(event, handler, prepend=True)

    def remove_listener(self, event: str, handler: Callable) -> None:
        if handler in self._get_listeners(event):
            self._events[event].remove(handler)
            self.emit('remove_listener', event, handler)

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        if event is not None:
            self._events.pop(event, None)
        else:
            self._events.clear()

    def off(self, event: str, handler: Callable) -> None:
        self.remove_listener(event, handler)

    def once(self, event: str, handler: Optional[Callable] = None) -> Callable:
        def wrapper(fn: Callable) -> Callable:
            @wraps(fn)
            def remove_then_run(*args: Any, **kwargs: Any) -> Any:
                self.remove_listener(event, remove_then_run)
                return fn(*args, **kwargs)

            self.add_listener(event, remove_then_run)
            return remove_then_run

        if handler is not None:
            return wrapper(handler)

        return wrapper

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        handlers = self._get_listeners(event)

        for handler in handlers:
            handler(*args, **kwargs)

        return len(handlers) > 0
