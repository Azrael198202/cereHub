from __future__ import annotations

from typing import Any

from core.config.config_loader import MODELS
from core.models.registry.provider_registry import ProviderRegistry
from core.models.resource_preparer import ModelResourcePreparer


class ModelRouter:
    """Routes model requests through provider registry and runtime preparation."""

    def __init__(self) -> None:
        self.provider_registry = ProviderRegistry()
        self.resource_preparer = ModelResourcePreparer()

    def complete_intent(self, text: str) -> dict[str, Any]:
        """Complete intent classification using configured primary and fallback models."""

        return self.complete_json(task_type="intent", user_prompt=text, system_prompt=self._intent_prompt())

    def complete_json(
        self,
        task_type: str,
        user_prompt: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Complete a JSON task using configured model routing."""

        config = MODELS[task_type]
        primary = config["primary"]
        fallback = config.get("fallback")

        try:
            return self._call_model(primary, system_prompt, user_prompt)
        except Exception as exc:
            print("primary model failed:", exc)

            if fallback:
                return self._call_model(fallback, system_prompt, user_prompt)

            raise

    def _call_model(self, model_config: dict, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        provider_name = model_config["provider"]
        model_name = model_config["model"]

        preparation = self.resource_preparer.prepare(
            provider=provider_name,
            model=model_name,
            prepare_runtime=model_config.get("prepare_runtime", True),
        )

        if not preparation["provider_ready"] or not preparation["model_ready"]:
            raise RuntimeError(f"Model resource is not ready: {provider_name}/{model_name}")

        provider = self.provider_registry.load(provider_name)

        result = provider.complete_json(
            model=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=model_config.get("temperature", 0.1),
        )

        if float(result.get("confidence", 1.0)) < model_config.get("min_confidence", 0.7):
            raise ValueError("Low confidence model result")

        return result

    def _intent_prompt(self) -> str:
        return (
            "You are an intent classifier.\n"
            "Return ONLY one valid JSON object.\n"
            "No markdown. No explanation.\n"
            "The JSON must include: intent_id, intent_type, name, description, confidence, "
            "entities, constraints, expected_outcome, requires_clarification, "
            "clarification_questions, source_text.\n"
            "intent_type must be either normal_intent or agent_creation_intent."
        )