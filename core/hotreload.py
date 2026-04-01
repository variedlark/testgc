from __future__ import annotations

import os
import time
import threading
from pathlib import Path
from typing import Callable, Dict, Iterable, Set


class HotReloader:
    """A simple polling-based hot-reloader that watches file mtimes and calls
    the provided callback(Path) when a watched file changes. This avoids an
    external dependency and is suitable for development iteration.
    """

    def __init__(self, paths: Iterable[Path], callback: Callable[..., None], interval: float = 0.8) -> None:
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.interval = float(interval)
        self._mtimes: Dict[str, float] = {}
        self._initialized = False
        self._running = False
        self._thread: threading.Thread | None = None

    def _dispatch(self, path: Path, change_type: str) -> None:
        try:
            self.callback(path, change_type)
        except TypeError:
            # Backward compatibility for callbacks expecting only a path
            self.callback(path)
        except Exception as ex:
            print(f"HotReloader callback failed: {ex}")

    def _scan_once(self) -> None:
        seen: Set[str] = set()
        for base in self.paths:
            if not base.exists():
                continue
            for root, _, files in os.walk(base):
                for fn in files:
                    if not (fn.endswith(".py") or fn.endswith(".json") or fn.endswith(".png") or fn.endswith(".wav")):
                        continue
                    full = os.path.join(root, fn)
                    seen.add(full)
                    try:
                        m = os.path.getmtime(full)
                    except OSError:
                        continue
                    prev = self._mtimes.get(full)
                    if prev is None:
                        self._mtimes[full] = m
                        if self._initialized:
                            self._dispatch(Path(full), "created")
                    elif m != prev:
                        self._mtimes[full] = m
                        self._dispatch(Path(full), "modified")

        if self._initialized:
            removed = [k for k in self._mtimes if k not in seen]
            for full in removed:
                self._mtimes.pop(full, None)
                self._dispatch(Path(full), "deleted")
        else:
            self._initialized = True

    def _loop(self) -> None:
        while self._running:
            self._scan_once()
            time.sleep(self.interval)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
