from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path


class ModelRuntimeRegistry:
    """Stores runtime model availability snapshots."""

    def __init__(self, path: str = "runtime/model_registry.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register_ready(self, provider: str, model: str, payload: dict) -> dict:
        """Register a model as ready or not ready."""

        data = self._load()
        key = f"{provider}/{model}"
        data[key] = {
            "provider": provider,
            "model": model,
            "status": "ready" if payload.get("ready") else "not_ready",
            "checked_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data[key]

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
