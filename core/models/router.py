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

        return self.complete_json(
            task_type="intent",
            user_prompt=text,
            system_prompt=self._intent_prompt(),
        )

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

    def _call_model(
        self,
        model_config: dict,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        """Prepare model runtime, dynamically load provider, then call model."""

        provider_name = model_config["provider"]
        model_name = model_config["model"]

        preparation = self.resource_preparer.prepare(
            provider=provider_name,
            model=model_name,
            prepare_runtime=model_config.get("prepare_runtime", True),
        )

        if not preparation["provider_ready"] or not preparation["model_ready"]:
            raise RuntimeError(
                f"Model resource is not ready: {provider_name}/{model_name}"
            )

        provider = self.provider_registry.load(provider_name)

        try:
            result = provider.complete_json(
                model=model_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=model_config.get("temperature", 0.1),
            )
        except Exception as exc:
            # If Ollama still reports model-not-found, force preparation once more.
            # This handles stale /api/tags, first pull delay, or incomplete runtime state.
            if provider_name == "ollama" and "not found" in str(exc).lower():
                preparation = self.resource_preparer.prepare(
                    provider=provider_name,
                    model=model_name,
                    prepare_runtime=True,
                    force=True,
                )

                if not preparation["provider_ready"] or not preparation["model_ready"]:
                    raise RuntimeError(
                        f"Model resource is still not ready: {provider_name}/{model_name}"
                    ) from exc

                result = provider.complete_json(
                    model=model_name,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=model_config.get("temperature", 0.1),
                )
            else:
                raise

        min_confidence = model_config.get("min_confidence")
        if min_confidence is not None:
            if float(result.get("confidence", 1.0)) < float(min_confidence):
                raise ValueError("Low confidence model result")

        return result

    def _intent_prompt(self) -> str:
        """Prompt used for intent classification."""

        return (
            "You are an intent classifier.\n"
            "Return ONLY one valid JSON object.\n"
            "No markdown. No explanation.\n"
            "The JSON must include these required fields exactly:\n"
            "- intent_id: non-empty string, generate one if needed, for example intent_model_001\n"
            "- intent_type: normal_intent or agent_creation_intent\n"
            "- name: snake_case intent name\n"
            "- description: short description\n"
            "- confidence: number between 0 and 1\n"
            "- entities: object\n"
            "- constraints: object\n"
            "- expected_outcome: non-empty string array\n"
            "- requires_clarification: boolean\n"
            "- clarification_questions: array\n"
            "- source_text: original user text\n"
            "If intent_type is agent_creation_intent, entities.agent_role is required.\n"
        )