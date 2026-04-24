from __future__ import annotations

from core.config.config_loader import MODELS
from core.models.registry.model_runtime_registry import ModelRuntimeRegistry

"""ModelSelector combines configured candidates with runtime-registered models."""
class ModelSelector:
    """Combines configured candidates with runtime-registered models."""

    def __init__(self) -> None:
        self.runtime_registry = ModelRuntimeRegistry()

    def get_candidates(self, task_type: str) -> list[dict]:
        """Return config candidates plus runtime-ready candidates."""

        config = MODELS[task_type]
        candidates: list[dict] = []

        if "candidates" in config:
            candidates.extend(config["candidates"])
        else:
            if "primary" in config:
                candidates.append(config["primary"])
            if "fallback" in config:
                candidates.append(config["fallback"])

        candidates.extend(self._runtime_candidates(task_type))
        return self._dedupe(candidates)

    def _runtime_candidates(self, task_type: str) -> list[dict]:
        runtime_models = self.runtime_registry.list_ready_for_task(task_type)
        candidates = []

        for item in runtime_models:
            provider = item.get("provider")
            model = item.get("model")
            if not provider or not model:
                continue

            candidates.append({
                "name": item.get("display_name") or f"{provider}_{model}",
                "provider": provider,
                "model": model,
                "temperature": 0.1,
                "min_confidence": 0.5,
                "prepare_runtime": False,
                "source": "runtime_registry",
                "local_path": item.get("local_path"),
                "format": item.get("format"),
            })

        return candidates

    def _dedupe(self, candidates: list[dict]) -> list[dict]:
        seen: set[tuple[str, str]] = set()
        result: list[dict] = []

        for candidate in candidates:
            key = (candidate.get("provider", ""), candidate.get("model", ""))
            if key in seen:
                continue
            seen.add(key)
            result.append(candidate)

        return result
