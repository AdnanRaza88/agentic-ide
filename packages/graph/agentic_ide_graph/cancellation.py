"""Cancellation token implementation."""

from __future__ import annotations

import threading


class SimpleCancellationToken:
    def __init__(self) -> None:
        self._cancelled = False
        self._lock = threading.Lock()

    def is_cancelled(self) -> bool:
        with self._lock:
            return self._cancelled

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True
