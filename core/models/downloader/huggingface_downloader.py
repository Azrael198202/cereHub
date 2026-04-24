from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from core.contracts.model_resource import ModelInstallResult, ModelResource


class HuggingFaceDownloader:
    """Downloads Hugging Face models into runtime/models/huggingface."""

    def __init__(self, base_dir: str = "runtime/models/huggingface") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def download(self, resource: ModelResource) -> ModelInstallResult:
        """Download a Hugging Face model snapshot and return install result."""

        if resource.provider != "huggingface":
            raise ValueError(f"Unsupported provider: {resource.provider}")

        local_path = Path(resource.local_path) if resource.local_path else self._default_local_path(resource.model)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            downloaded_path = snapshot_download(
                repo_id=resource.model,
                local_dir=str(local_path),
                local_dir_use_symlinks=False,
            )
            return ModelInstallResult(
                resource_id=resource.resource_id,
                provider=resource.provider,
                model=resource.model,
                local_path=downloaded_path,
                status="ready",
                ready=True,
                message="Model downloaded successfully.",
                metadata={"format": resource.format},
            )
        except Exception as exc:
            return ModelInstallResult(
                resource_id=resource.resource_id,
                provider=resource.provider,
                model=resource.model,
                local_path=str(local_path),
                status="failed",
                ready=False,
                message=str(exc),
                metadata={"format": resource.format},
            )

    def _default_local_path(self, repo_id: str) -> Path:
        safe_name = repo_id.replace("/", "_").replace(":", "_")
        return self.base_dir / safe_name
