from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Deque, Optional
from uuid import uuid4


class RuntimeProgressStore:
    """In-memory store for recent runtime progress events."""

    def __init__(self, max_events: int = 1000) -> None:
        self._events: Deque[dict[str, Any]] = deque(maxlen=max_events)
        self._lock = Lock()

    def emit(
        self,
        event_type: str,
        message: str,
        status: str = "running",
        operation_id: Optional[str] = None,
        progress: Optional[float] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record and return a runtime progress event."""

        event = {
            "id": str(uuid4()),
            "type": event_type,
            "message": message,
            "status": status,
            "operation_id": operation_id,
            "progress": progress,
            "payload": payload or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._events.append(event)

        return event

    def list_events(self, limit: int = 200) -> list[dict[str, Any]]:
        """Return recent events ordered from oldest to newest."""

        with self._lock:
            events = list(self._events)

        if limit <= 0:
            return []
        return events[-limit:]

    def latest(self) -> Optional[dict[str, Any]]:
        """Return the latest event if one exists."""

        with self._lock:
            if not self._events:
                return None
            return self._events[-1]

    def clear(self) -> None:
        """Clear all recorded progress events."""

        with self._lock:
            self._events.clear()


progress_store = RuntimeProgressStore()
