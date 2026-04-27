from __future__ import annotations

from typing import Any, Optional

from core.models.registry.provider_registry import ProviderRegistry
from core.models.resource_preparer import ModelResourcePreparer
from core.models.selector.model_selector import ModelSelector


class ModelRouter:
    """Routes requests through configured and runtime-registered models."""

    def __init__(self) -> None:
        self.selector = ModelSelector()
        self.provider_registry = ProviderRegistry()
        self.resource_preparer = ModelResourcePreparer()

    async def complete_intent(self, text: str) -> dict[str, Any]:
        """Complete intent classification."""

        return await self.complete_json(
            task_type="intent",
            user_prompt=text,
            system_prompt=self._intent_prompt(),
        )

    async def complete_json(self, task_type: str, user_prompt: str, system_prompt: str) -> dict[str, Any]:
        """Complete a JSON task using all candidates."""

        last_error: Optional[Exception] = None

        for model_config in self.selector.get_candidates(task_type):
            try:
                return await self._call_model(model_config, system_prompt, user_prompt)
            except Exception as exc:
                last_error = exc
                print("model failed:", model_config.get("provider"), model_config.get("model"), exc)

        if last_error:
            raise last_error

        raise RuntimeError(f"No model candidates available for task_type={task_type}")

    async def _call_model(self, model_config: dict, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        provider_name = model_config["provider"]
        model_name = model_config["model"]

        preparation = await self.resource_preparer.prepare(
            provider=provider_name,
            model=model_name,
            prepare_runtime=model_config.get("prepare_runtime", True),
        )

        if not preparation["provider_ready"] or not preparation["model_ready"]:
            raise RuntimeError(f"Model resource is not ready: {provider_name}/{model_name}")

        provider = await self.provider_registry.load(provider_name, model_config=model_config)

        result = await provider.complete_json(
            model=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=model_config.get("temperature", 0.1),
        )

        min_confidence = model_config.get("min_confidence")
        if min_confidence is not None:
            if float(result.get("confidence", 1.0)) < float(min_confidence):
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
            "intent_type must be either normal_intent or agent_creation_intent.\n"
            "If intent_type is agent_creation_intent, entities.agent_role is required.\n"
        )
