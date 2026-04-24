from __future__ import annotations

import json
from pathlib import Path


class RuntimeResourceRegistry:
    """Stores runtime resource and capability snapshots."""

    def __init__(self, path: str = "runtime/runtime_resources.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register(self, resource_id: str, payload: dict) -> dict:
        """Register or update a runtime resource snapshot."""

        data = self._load()
        data[resource_id] = payload
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data[resource_id]

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
