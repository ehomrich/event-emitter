# event-emitter
Python port of [EventEmitter from Node.js](https://nodejs.org/api/events.html#events_class_eventemitter), for learning purposes.

This project is under (slow) development and needless to say its use is **not** recommended. You've been warned.

## Usage

```python
from event_emitter import EventEmitter

emitter = EventEmitter()

@emitter.on('greet')
def greeting(name: str, age: int):
  print(f"Hey there! I'm {name} and I'm {age} years old.")

emitter.emit('greet', name='Émerson', age=25)
# Hey there! I'm Émerson and I'm 24 years old.
```

## API

### `EventEmitter([max_listeners])`
An EventEmitter is a plain old Python object.

The initializer can optionally receive a `max_listeners` argument, which defines the soft limit of listeners for each event.

Instances of `EventEmitter` emit the events `new_listener` and `remove_listener` whenever new listeners are registered and when existing listeners are removed, respectivelly. See [default events](#default-events) for more info.

### `len(emitter)`
Returns the number of events registered, regardless of the number of listeners attached.

### `emitter['event_name']`
Returns the (mutable) list of listeners of the specified event. Raises a `KeyError` if the event name does not exist.

For an immutable and fail-safe option, use the [listeners](#listenersevent) method.

### `del emitter['event_name']`
Removes the specified event and its list of listeners. Raises a `KeyError` if the event name does not exist.

For a fail-safe option, use the [remove_listeners](#remove_listenerevent-handler) method.

### `'event_name' in emitter`
Returns `True` if the event name exists, else `False`.

### `max_listeners`

Getter for the number of listeners allowed for each event (default `10`).

### `set_max_listeners(value)`

Defines the soft limit of listeners for each event.

The argument must be a non-negative integer.

```python
emitter.set_max_listeners(5) # ok
emitter.set_max_listeners(0) # also ok

emitter.set_max_listeners('3') # TypeError
emitter.set_max_listeners(-7) # ValueError
```

Events whose listeners count were already greater than the new maximum number remain unchanged, but additions of new listeners are subject to the check.

### `event_names()`

Returns a tuple listing the events for which the emitter has at least one listener attached.

```python
emitter.event_names()
# ('greet',)
```

### `listeners(event)`

Returns a tuple of listeners for the specified event, if it exists.

```python
emitter.listeners('greet')
# (<function greeting at 0x...>,)

emitter.listeners('nonexistent')
# ()
```

### `count(event)`

Returns the number of listeners attached to the specified event. Returns `0` it the event doesn't exist.

```python
emitter.count('greet')
# 1
```
### `add_listener(event, handler)`

Appends the handler function to the list of listeners for the specified event.

No checks are made to avoid duplicates. Multiple calls with the same handler result in the handler being added multiple times.

Emit a `new_listener` event **before** the listener is added.

```python
def timeout_callback(ctx):
  print('Read timeout, exiting...', ctx)

emitter.add_listener('timeout', timeout_callback)
```

### `on(event, handler)`

Alias for `add_listener`.

This method can be used as a decorator:

```python
@emitter.on('post_save')
def post_save_hook(sender, instance):
    model = sender.__class__.__name__
    print(f'Instance of {model} saved with ID {instance.id}')
```

### `once(event, handler)`

Adds as a **one-time** listener for the specified event.

The handler is wrapped and removes itself before being executed the next time the event is triggered.

Uses `add_listener` and `remove_listener` methods under the hood, but the removal event behavior is different. See [default events](#default-events) for more info.

As well as `on`, this method can also be used as a decorator:

```python
@emitter.once('disconnected')
def disconnect_callback(reason):
    print('Connection lost', reason)
```

### `prepend_listener(event, handler)`

Adds the handler function to the beginning of the list of listeners for the specified event.

Rules and behavior are the same as the `add_listener` method.

### `remove_listener(event, handler)`

Removes the handler from the list of listeners for the specified event.

Removes at most one handler instance from the listeners list, if it exists.

Emit a `remove_listener` event **after** the listener is removed.

```python
emitter.remove_listener('greet', greeting)
```

### `off(event, handler)`

Alias for `remove_listener`.

```python
emitter.off('timeout', timeout_callback)
```

### `remove_all_listeners([event])`

Remove all listeners, or those of the specified event (the event name entry is also removed).

No event is emitted.

```python
# Clear the listener store
emitter.remove_all_listeners()

# Only remove 'disconnected' listeners
emitter.remove_all_listeners('disconnected')
```

### `emit(event, *args, **kwargs)`

Synchronously calls each of the listeners attached to the specified event, in the order they were registered. The supplied positional and keyword arguments are passed to each listener.

Return `True` if the event had listeners, `False` otherwise.

No errors raised by listeners will be handled.

```python
emitter.emit('post_save', sender=Book, instance=obj)
# Instance of Book saved with ID 1877
```

## Default events

### `new_listener`

Fired whenever a new listener is added to an event, with the event name and a reference to the listener.

The event is emitted **before** the listener is added.

### `remove_listener`

Fired when a listener is removed from an event, with the event name and a reference to the removed listener.

Emitted **after** the listener is removed.

The exception is the `once` method. Since the function to be removed is actually the wrapper that removes the handler, the event is emitted after the wrapper, but *before* the actual handler).

## TODO

- [x] Implement basic methods
- [x] Implement dict-like interface
- [x] Add type hints
- [x] Add decorator functionality to `on` and `once` methods
- [x] Implement basic emission logic
- [x] Add events for new and removed listeners
- [ ] Add max listeners check
- [ ] Review emission and dispatch flow
- [ ] Add `asyncio` support
- [ ] Add docstrings
- [ ] Write tests!

## License
MIT