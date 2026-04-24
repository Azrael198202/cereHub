from __future__ import annotations

import importlib
from typing import Any

from core.config.config_loader import SETTINGS


class ProviderRegistry:
    """Loads provider instances by provider name."""

    BUILTIN_PROVIDERS = {
        "ollama": "core.models.providers.ollama_provider.OllamaProvider",
        "mock": "core.models.providers.mock_provider.MockProvider",
    }

    def load(self, provider_name: str) -> Any:
        """Load a provider instance dynamically."""

        if provider_name not in self.BUILTIN_PROVIDERS:
            raise KeyError(f"Unknown provider: {provider_name}")

        class_path = self.BUILTIN_PROVIDERS[provider_name]
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        provider_cls = getattr(module, class_name)

        if provider_name == "ollama":
            return provider_cls(api_base=SETTINGS["ollama"]["api_base"])

        return provider_cls()
