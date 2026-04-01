from __future__ import annotations

from typing import Any, Callable, Dict


class ServiceContainer:
    """A minimal dependency container for registering and resolving services.

    Register either singletons (pre-created objects) or factories (callable that
    returns a new instance). Factories are cached on first resolve.
    """

    def __init__(self) -> None:
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, key: str, instance: Any) -> None:
        self._singletons[key] = instance

    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
        self._factories[key] = factory

    def resolve(self, key: str) -> Any:
        if key in self._singletons:
            return self._singletons[key]
        if key in self._factories:
            instance = self._factories[key]()
            # cache factory result as singleton for future resolves
            self._singletons[key] = instance
            return instance
        raise KeyError(f"Service not found: {key}")

    def unregister(self, key: str) -> None:
        self._singletons.pop(key, None)
        self._factories.pop(key, None)

    def clear(self) -> None:
        self._singletons.clear()
        self._factories.clear()
