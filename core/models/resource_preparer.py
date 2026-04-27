from __future__ import annotations

from typing import Any

import yaml

from core.config.config_loader import BASE_DIR, SETTINGS
from core.contracts.runtime_resource import RuntimeResource
from core.environment.workflows.prepare_runtime_resource import PrepareRuntimeResourceWorkflow
from core.models.registry.model_runtime_registry import ModelRuntimeRegistry


class ModelResourcePreparer:
    """Prepares runtime resources required by model providers."""

    def __init__(self) -> None:
        self.workflow = PrepareRuntimeResourceWorkflow()
        self.model_registry = ModelRuntimeRegistry()
        self._litellm_backing_cache: dict[str, tuple[str, str]] | None = None

    async def prepare(
        self,
        provider: str,
        model: str,
        prepare_runtime: bool = True,
        force: bool = False,
    ) -> dict:
        """Prepare provider runtime and model before a model call."""

        if not prepare_runtime:
            return {
                "provider_ready": True,
                "model_ready": True,
                "provider_result": {},
                "model_result": {},
            }

        if provider == "ollama":
            return await self._prepare_ollama(model=model, force=force)

        if provider == "litellm":
            return await self._prepare_litellm(model=model, force=force)

        return {
            "provider_ready": True,
            "model_ready": True,
            "provider_result": {},
            "model_result": {},
        }

    async def _prepare_ollama(self, model: str, force: bool = False) -> dict:
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

        provider_result = await self.workflow.run(provider_resource, force=force)
        model_result = await self.workflow.run(model_resource, force=force)

        payload = {
            "ready": provider_result.ready and model_result.ready,
            "provider_ready": provider_result.ready,
            "model_ready": model_result.ready,
            "provider_result": provider_result.model_dump(),
            "model_result": model_result.model_dump(),
        }
        await self.model_registry.register_ready("ollama", model, payload)

        return payload

    async def _prepare_litellm(self, model: str, force: bool = False) -> dict:
        api_base = SETTINGS["litellm"]["base_url"].rstrip("/")

        proxy_resource = RuntimeResource(
            resource_id="res_litellm_proxy",
            resource_type="external_model",
            name="litellm-proxy",
            provider="litellm",
            required=True,
            install_strategy=[],
            verification_command=None,
            healthcheck_url=f"{api_base}/models",
            dependencies=[],
            metadata={"role": "model_gateway"},
        )

        proxy_result = await self.workflow.run(proxy_resource, force=force)

        backing = self._resolve_litellm_backing_model(model)
        if not backing:
            return {
                "ready": proxy_result.ready,
                "provider_ready": proxy_result.ready,
                "model_ready": True,
                "provider_result": proxy_result.model_dump(),
                "model_result": {},
            }

        backing_provider, backing_model = backing
        if backing_provider != "ollama":
            raise RuntimeError(f"Unsupported LiteLLM backing provider: {backing_provider}")

        backing_result = await self._prepare_ollama(model=backing_model, force=force)
        payload = {
            "ready": proxy_result.ready and backing_result["model_ready"],
            "provider_ready": proxy_result.ready,
            "model_ready": backing_result["model_ready"],
            "provider_result": proxy_result.model_dump(),
            "model_result": backing_result,
            "backing_provider": backing_provider,
            "backing_model": backing_model,
        }
        if payload["ready"]:
            await self.model_registry.register_ready("litellm", model, payload)

        return payload

    def _resolve_litellm_backing_model(self, alias: str) -> tuple[str, str] | None:
        if self._litellm_backing_cache is None:
            self._litellm_backing_cache = self._load_litellm_backing_models()

        return self._litellm_backing_cache.get(alias)

    def _load_litellm_backing_models(self) -> dict[str, tuple[str, str]]:
        config_path = BASE_DIR / "core/config/litellm.config.yaml"
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        model_list = payload.get("model_list") or []

        result: dict[str, tuple[str, str]] = {}
        for item in model_list:
            if not isinstance(item, dict):
                continue

            alias = item.get("model_name")
            params = item.get("litellm_params") or {}
            backing_model = self._parse_litellm_backing_model(params)
            if alias and backing_model:
                result[alias] = backing_model

        return result

    def _parse_litellm_backing_model(self, params: dict[str, Any]) -> tuple[str, str] | None:
        model = params.get("model")
        if not isinstance(model, str):
            return None

        for prefix in ("ollama_chat/", "ollama/"):
            if model.startswith(prefix):
                return ("ollama", model.removeprefix(prefix))

        return None
