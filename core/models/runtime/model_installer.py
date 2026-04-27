from __future__ import annotations

import json
from pathlib import Path

from core.contracts.model_resource import ModelResource
from core.models.downloader.huggingface_downloader import HuggingFaceDownloader
from core.models.registry.model_runtime_registry import ModelRuntimeRegistry

"""Model installer for installing/downloading model resources and registering them at runtime."""
class ModelInstaller:
    """Installs/downloads model resources and registers them at runtime."""

    def __init__(self) -> None:
        self.registry = ModelRuntimeRegistry()
        self.hf_downloader = HuggingFaceDownloader()

    async def install_from_file(self, path: str) -> dict:
        """Install a model from a model resource JSON file."""

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        resource = ModelResource(**payload)
        return await self.install(resource)

    async def install(self, resource: ModelResource) -> dict:
        """Install/download a model resource and register it."""

        if resource.provider == "huggingface":
            result = await self.hf_downloader.download(resource)
            return await self.registry.register_resource(resource, result)

        raise ValueError(f"Unsupported model provider for installer: {resource.provider}")


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--resource", required=True)
    args = parser.parse_args()

    result = await ModelInstaller().install_from_file(args.resource)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
