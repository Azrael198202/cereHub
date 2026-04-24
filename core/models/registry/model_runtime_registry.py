from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from core.contracts.model_resource import ModelInstallResult, ModelResource

"""Runtime registry for downloaded, verified, or discovered models."""
class ModelRuntimeRegistry:
    """Runtime registry for downloaded, verified, or discovered models."""

    def __init__(self, path: str = "runtime/model_registry.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register_resource(self, resource: ModelResource, install_result: ModelInstallResult) -> dict:
        """Register model resource with install result."""

        data = self._load()
        key = self._key(resource.provider, resource.model)
        data[key] = {
            "resource_id": resource.resource_id,
            "provider": resource.provider,
            "model": resource.model,
            "display_name": resource.display_name or resource.model,
            "local_path": install_result.local_path or resource.local_path,
            "format": resource.format,
            "capabilities": resource.capabilities,
            "recommended_tasks": resource.recommended_tasks,
            "tags": resource.tags,
            "status": "ready" if install_result.ready else "failed",
            "ready": install_result.ready,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "message": install_result.message,
            "metadata": {**resource.metadata, **install_result.metadata},
        }
        self._save(data)
        return data[key]

    def register_ready(self, provider: str, model: str, payload: dict) -> dict:
        """Register a provider/model pair as ready or not ready."""

        data = self._load()
        key = self._key(provider, model)
        data[key] = {
            "provider": provider,
            "model": model,
            "status": "ready" if payload.get("ready") else "not_ready",
            "ready": bool(payload.get("ready")),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self._save(data)
        return data[key]

    def list_ready_for_task(self, task_type: str) -> list[dict]:
        """Return ready runtime models suitable for a task type."""

        results = []
        for item in self._load().values():
            if item.get("status") != "ready" and not item.get("ready"):
                continue
            capabilities = item.get("capabilities", [])
            recommended_tasks = item.get("recommended_tasks", [])
            if task_type in capabilities or task_type in recommended_tasks:
                results.append(item)
        return results

    def list_all(self) -> dict:
        """Return all registered models."""
        return self._load()

    def _key(self, provider: str, model: str) -> str:
        return f"{provider}/{model}"

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")