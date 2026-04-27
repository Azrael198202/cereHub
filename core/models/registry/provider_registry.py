from __future__ import annotations

import importlib
from typing import Any, Optional

from core.config.config_loader import SETTINGS

"""Registry for loading provider instances by name."""
class ProviderRegistry:
    """Loads provider instances by provider name."""

    BUILTIN_PROVIDERS = {
        "ollama": "core.models.providers.ollama_provider.OllamaProvider",
        "mock": "core.models.providers.mock_provider.MockProvider",
        "huggingface": "core.models.providers.huggingface_provider.HuggingFaceProvider",
    }

    async def load(self, provider_name: str, model_config: Optional[dict] = None) -> Any:
        """Load a provider instance dynamically."""

        if provider_name not in self.BUILTIN_PROVIDERS:
            raise KeyError(f"Unknown provider: {provider_name}")

        class_path = self.BUILTIN_PROVIDERS[provider_name]
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        provider_cls = getattr(module, class_name)

        if provider_name == "ollama":
            return provider_cls(api_base=SETTINGS["ollama"]["api_base"])

        if provider_name == "huggingface":
            local_path = model_config.get("local_path") if model_config else None
            return provider_cls(local_path=local_path)

        return provider_cls()
