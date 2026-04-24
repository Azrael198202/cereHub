from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from core.contracts.trace import TraceModel


class TraceStore:
    """Simple JSONL-based trace store.

    It can later be replaced by PostgreSQL, Elasticsearch, or another backend
    without changing callers.
    """

    def __init__(self, path: str = "runtime/traces.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, trace: TraceModel) -> None:
        """Append one trace record."""

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trace.model_dump(), ensure_ascii=False) + "\n")

    def append_many(self, traces: Iterable[TraceModel]) -> None:
        """Append multiple trace records."""

        with self.path.open("a", encoding="utf-8") as f:
            for trace in traces:
                f.write(json.dumps(trace.model_dump(), ensure_ascii=False) + "\n")

    def list_all(self) -> list[dict]:
        """Load all trace records."""

        if not self.path.exists():
            return []

        records: list[dict] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records

    def find_by_workflow(self, workflow_id: str) -> list[dict]:
        """Find traces by workflow id."""

        return [record for record in self.list_all() if record.get("workflow_id") == workflow_id]

    def find_by_intent(self, intent_id: str) -> list[dict]:
        """Find traces by intent id."""

        return [record for record in self.list_all() if record.get("intent_id") == intent_id]

    def clear(self) -> None:
        """Delete all stored traces."""

        if self.path.exists():
            self.path.unlink()
