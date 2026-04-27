import importlib


class ProviderRegistry:
    """Loads provider classes by provider name."""

    BUILTIN_PROVIDERS = {
        "ollama": "core.models.providers.ollama_provider.OllamaProvider",
        "mock": "core.models.providers.mock_provider.MockProvider",
    }

    async def load(self, provider_name: str, settings: dict):
        path = self.BUILTIN_PROVIDERS[provider_name]
        module_path, class_name = path.rsplit(".", 1)

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)

        if provider_name == "ollama":
            return cls(api_base=settings["ollama"]["api_base"])

        return cls()