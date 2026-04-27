from __future__ import annotations

from typing import Any

from core.config.config_loader import MODELS
from core.models.registry.model_runtime_registry import ModelRuntimeRegistry


class ModelSelector:
    """Combines configured candidates with runtime-registered models and ranks them."""

    DEFAULT_METRICS = {
        "local-intent": {"cost": 0.0, "latency_ms": 1200, "success_rate": 0.72},
        "local-intent-instruct": {"cost": 0.0, "latency_ms": 1800, "success_rate": 0.76},
        "local-workflow": {"cost": 0.0, "latency_ms": 6000, "success_rate": 0.65},
        "local-reasoning": {"cost": 0.0, "latency_ms": 8000, "success_rate": 0.68},
        "cloud-chat": {"cost": 0.3, "latency_ms": 2500, "success_rate": 0.90},
        "cloud-reasoning": {"cost": 0.8, "latency_ms": 3500, "success_rate": 0.95},

        # models.json
        "qwen3:4b": {"cost": 0.0, "latency_ms": 5000, "success_rate": 0.68},
        "qwen3:4b-instruct": {"cost": 0.0, "latency_ms": 4500, "success_rate": 0.72},
        "qwen3:8b": {"cost": 0.0, "latency_ms": 9000, "success_rate": 0.70},
        "deepseek-r1:7b": {"cost": 0.0, "latency_ms": 10000, "success_rate": 0.72},
        "gpt-4o-mini": {"cost": 0.3, "latency_ms": 2500, "success_rate": 0.90},
    }

    TASK_POLICY = {
        "intent": {
            "cost_weight": 0.2,
            "latency_weight": 0.5,
            "success_weight": 0.3,
            "prefer_local": True,
        },
        "workflow": {
            "cost_weight": 0.2,
            "latency_weight": 0.3,
            "success_weight": 0.5,
            "prefer_local": True,
        },
        "chat": {
            "cost_weight": 0.3,
            "latency_weight": 0.2,
            "success_weight": 0.5,
            "prefer_local": False,
        },
        "code_generation": {
            "cost_weight": 0.1,
            "latency_weight": 0.1,
            "success_weight": 0.8,
            "prefer_local": False,
        },
        "complex_reasoning": {
            "cost_weight": 0.1,
            "latency_weight": 0.1,
            "success_weight": 0.8,
            "prefer_local": False,
        },
    }

    LOCAL_PROVIDERS = {"ollama", "huggingface", "mock"}

    def __init__(self) -> None:
        self.runtime_registry = ModelRuntimeRegistry()

    def get_candidates(self, task_type: str) -> list[dict[str, Any]]:
        """Return config candidates plus runtime-ready candidates, then rank them."""

        config = MODELS[task_type]
        candidates: list[dict[str, Any]] = []

        if "candidates" in config:
            candidates.extend(config["candidates"])
        else:
            if "primary" in config:
                candidates.append(config["primary"])
            if "fallback" in config:
                candidates.append(config["fallback"])

        candidates.extend(self._runtime_candidates(task_type))

        deduped = self._dedupe(candidates)

        ''' first_success smart_select'''
        strategy = config.get("strategy", "smart_select")

        if strategy in {"smart_select", "smart", "ranked"}:
            return self._rank(task_type, deduped)

        # first_success
        return deduped

    def _runtime_candidates(self, task_type: str) -> list[dict[str, Any]]:
        runtime_models = self.runtime_registry.list_ready_for_task(task_type)
        candidates: list[dict[str, Any]] = []

        for item in runtime_models:
            provider = item.get("provider")
            model = item.get("model")
            if not provider or not model:
                continue

            candidates.append(
                {
                    "name": item.get("display_name") or f"{provider}_{model}",
                    "provider": provider,
                    "model": model,
                    "temperature": 0.1,
                    "min_confidence": 0.5,
                    "prepare_runtime": False,
                    "source": "runtime_registry",
                    "local_path": item.get("local_path"),
                    "format": item.get("format"),
                    "metrics": item.get("metrics", {}),
                }
            )

        return candidates

    def _dedupe(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        result: list[dict[str, Any]] = []

        for candidate in candidates:
            key = (candidate.get("provider", ""), candidate.get("model", ""))
            if key in seen:
                continue
            seen.add(key)
            result.append(candidate)

        return result

    def _rank(
        self,
        task_type: str,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        policy = self.TASK_POLICY.get(task_type, self.TASK_POLICY["chat"])

        ranked: list[dict[str, Any]] = []

        for candidate in candidates:
            model = candidate.get("model", "")
            provider = candidate.get("provider", "")

            metrics = self._resolve_metrics(candidate)

            cost = float(metrics.get("cost", 0.5))
            latency_ms = float(metrics.get("latency_ms", 5000))
            success_rate = float(metrics.get("success_rate", 0.5))

            score = self._calculate_score(
                cost=cost,
                latency_ms=latency_ms,
                success_rate=success_rate,
                provider=provider,
                policy=policy,
            )

            item = dict(candidate)
            item["_selection_score"] = round(score, 4)
            item["_selection_reason"] = (
                f"model={model}, provider={provider}, "
                f"cost={cost}, latency_ms={latency_ms}, "
                f"success_rate={success_rate}"
            )
            ranked.append(item)

        ranked.sort(key=lambda x: x.get("_selection_score", 0), reverse=True)
        return ranked

    def _resolve_metrics(self, candidate: dict[str, Any]) -> dict[str, float]:
        inline_metrics = candidate.get("metrics") or {}
        if inline_metrics:
            return inline_metrics

        model = candidate.get("model", "")
        name = candidate.get("name", "")

        if model in self.DEFAULT_METRICS:
            return self.DEFAULT_METRICS[model]

        if name in self.DEFAULT_METRICS:
            return self.DEFAULT_METRICS[name]

        provider = candidate.get("provider", "")

        if provider in self.LOCAL_PROVIDERS:
            return {
                "cost": 0.0,
                "latency_ms": 6000,
                "success_rate": 0.6,
            }

        if provider == "litellm":
            # Prepare for cases where the LiteLLM model is an alias such as local-intent / cloud-chat.
            return self.DEFAULT_METRICS.get(
                model,
                {
                    "cost": 0.4,
                    "latency_ms": 3500,
                    "success_rate": 0.85,
                },
            )

        return {
            "cost": 0.5,
            "latency_ms": 5000,
            "success_rate": 0.5,
        }

    def _calculate_score(
        self,
        cost: float,
        latency_ms: float,
        success_rate: float,
        provider: str,
        policy: dict[str, Any],
    ) -> float:
        cost_score = 1.0 - min(cost, 1.0)
        latency_score = 1.0 - min(latency_ms / 10000.0, 1.0)
        success_score = max(0.0, min(success_rate, 1.0))

        score = (
            cost_score * policy["cost_weight"]
            + latency_score * policy["latency_weight"]
            + success_score * policy["success_weight"]
        )

        if policy.get("prefer_local") and provider in self.LOCAL_PROVIDERS:
            score += 0.05

        return score