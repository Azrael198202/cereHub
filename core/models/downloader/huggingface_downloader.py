from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

from core.contracts.model_resource import ModelInstallResult, ModelResource
from core.runtime.progress import progress_store


class HuggingFaceDownloader:
    """Downloads Hugging Face models into runtime/models/huggingface with progress."""

    def __init__(self, base_dir: str = "runtime/models/huggingface") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def download(self, resource: ModelResource) -> ModelInstallResult:
        """Download a Hugging Face model snapshot and return install result."""

        if resource.provider != "huggingface":
            raise ValueError(f"Unsupported provider: {resource.provider}")

        local_path = Path(resource.local_path) if resource.local_path else self._default_local_path(resource.model)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        progress_store.emit(
            "hf_download_start",
            f"Downloading Hugging Face model: {resource.model}",
            status="running",
            operation_id=resource.resource_id,
            payload=resource.model_dump(),
        )

        try:
            downloaded_path = await snapshot_download(
                repo_id=resource.model,
                local_dir=str(local_path),
                local_dir_use_symlinks=False,
            )

            progress_store.emit(
                "hf_download_done",
                f"Downloaded Hugging Face model: {resource.model}",
                status="success",
                operation_id=resource.resource_id,
                progress=1.0,
                payload={"local_path": downloaded_path},
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
            progress_store.emit(
                "hf_download_failed",
                f"Failed to download Hugging Face model: {resource.model}",
                status="failed",
                operation_id=resource.resource_id,
                payload={"error": str(exc)},
            )

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