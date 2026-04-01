from collections import defaultdict, deque
from typing import Any, Callable, Deque, Dict, List


class _Subscription:
    def __init__(self, callback: Callable[[Any], None], priority: int = 0, once: bool = False) -> None:
        self.callback = callback
        self.priority = int(priority)
        self.once = bool(once)


class EventBus:
    """Enhanced event bus with prioritized listeners, one-shot subscriptions,
    and a pending queue for deferred emission.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[_Subscription]] = defaultdict(list)
        self._pending: Deque[tuple[str, Any]] = deque()

    def subscribe(self, event_name: str, callback: Callable[[Any], None], priority: int = 0, once: bool = False) -> None:
        """Subscribe to `event_name` with optional `priority` and `once` flag.

        Higher `priority` handlers are invoked first.
        """
        subs = self._subscribers[event_name]
        subs.append(_Subscription(callback, priority, once))
        subs.sort(key=lambda s: -s.priority)

    def subscribe_once(self, event_name: str, callback: Callable[[Any], None], priority: int = 0) -> None:
        self.subscribe(event_name, callback, priority=priority, once=True)

    def unsubscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        subs = self._subscribers.get(event_name, [])
        self._subscribers[event_name] = [s for s in subs if s.callback != callback]

    def emit(self, event_name: str, payload: Any = None) -> None:
        """Emit an event immediately to all subscribers."""
        subs = list(self._subscribers.get(event_name, []))
        to_remove: List[_Subscription] = []
        for s in subs:
            try:
                s.callback(payload)
            except Exception as ex:  # keep delivery robust
                print(f"Event handler for {event_name} raised: {ex}")
            if s.once:
                to_remove.append(s)
        if to_remove:
            self._subscribers[event_name] = [s for s in self._subscribers[event_name] if s not in to_remove]

    def emit_later(self, event_name: str, payload: Any = None) -> None:
        """Schedule an event to be emitted later; callers should invoke `process_pending`."""
        self._pending.append((event_name, payload))

    def process_pending(self) -> None:
        """Process all pending events (call from the game loop)."""
        while self._pending:
            event_name, payload = self._pending.popleft()
            self.emit(event_name, payload)

    def clear(self, event_name: str | None = None) -> None:
        if event_name is None:
            self._subscribers.clear()
        else:
            self._subscribers.pop(event_name, None)
