from __future__ import annotations

import os
import time
import threading
from pathlib import Path
from typing import Callable, Dict, Iterable


class HotReloader:
    """A simple polling-based hot-reloader that watches file mtimes and calls
    the provided callback(Path) when a watched file changes. This avoids an
    external dependency and is suitable for development iteration.
    """

    def __init__(self, paths: Iterable[Path], callback: Callable[[Path], None], interval: float = 0.8) -> None:
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.interval = float(interval)
        self._mtimes: Dict[str, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def _scan_once(self) -> None:
        for base in self.paths:
            if not base.exists():
                continue
            for root, _, files in os.walk(base):
                for fn in files:
                    if not (fn.endswith(".py") or fn.endswith(".json") or fn.endswith(".png") or fn.endswith(".wav")):
                        continue
                    full = os.path.join(root, fn)
                    try:
                        m = os.path.getmtime(full)
                    except OSError:
                        continue
                    prev = self._mtimes.get(full)
                    if prev is None:
                        self._mtimes[full] = m
                    elif m != prev:
                        self._mtimes[full] = m
                        try:
                            self.callback(Path(full))
                        except Exception as ex:
                            print(f"HotReloader callback failed: {ex}")

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
