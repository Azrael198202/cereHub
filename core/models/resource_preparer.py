from __future__ import annotations

from core.config.config_loader import SETTINGS
from core.contracts.runtime_resource import RuntimeResource
from core.environment.workflows.prepare_runtime_resource import PrepareRuntimeResourceWorkflow
from core.models.registry.model_runtime_registry import ModelRuntimeRegistry


class ModelResourcePreparer:
    """Prepares runtime resources required by model providers."""

    def __init__(self) -> None:
        self.workflow = PrepareRuntimeResourceWorkflow()
        self.model_registry = ModelRuntimeRegistry()

    def prepare(self, provider: str, model: str, prepare_runtime: bool = True) -> dict:
        """Prepare provider runtime and model before a model call."""

        if not prepare_runtime:
            return {
                "provider_ready": True,
                "model_ready": True,
                "provider_result": {},
                "model_result": {},
            }

        if provider == "ollama":
            return self._prepare_ollama(model)

        # External providers usually require API keys, not local installation.
        return {
            "provider_ready": True,
            "model_ready": True,
            "provider_result": {},
            "model_result": {},
        }

    def _prepare_ollama(self, model: str) -> dict:
        api_base = SETTINGS["ollama"]["api_base"].rstrip("/")

        provider_resource = RuntimeResource(
            resource_id="res_ollama_runtime",
            resource_type="software",
            name="ollama",
            provider="ollama",
            required=True,
            install_strategy=["install_provider_if_missing"],
            verification_command=["ollama", "--version"],
            healthcheck_url=f"{api_base}/api/tags",
            dependencies=[],
            metadata={"role": "local_llm_provider"},
        )

        model_resource = RuntimeResource(
            resource_id=f"res_ollama_model_{model.replace(':', '_').replace('/', '_')}",
            resource_type="local_model",
            name=model,
            provider="ollama",
            required=True,
            install_strategy=["pull_model"],
            verification_command=["ollama", "list"],
            healthcheck_url=f"{api_base}/api/tags",
            dependencies=["ollama"],
            metadata={"role": "local_llm_model"},
        )

        provider_result = self.workflow.run(provider_resource)
        model_result = self.workflow.run(model_resource)

        payload = {
            "ready": provider_result.ready and model_result.ready,
            "provider_ready": provider_result.ready,
            "model_ready": model_result.ready,
            "provider_result": provider_result.model_dump(),
            "model_result": model_result.model_dump(),
        }
        self.model_registry.register_ready("ollama", model, payload)

        return payload