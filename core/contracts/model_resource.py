from __future__ import annotations

from pydantic import BaseModel, Field

"""Model resource definitions for model management."""
class ModelResource(BaseModel):
    """A model resource that can be downloaded, verified, and registered."""

    resource_id: str
    provider: str
    model: str
    display_name: str | None = None
    local_path: str | None = None
    format: str = "unknown"
    capabilities: list[str] = Field(default_factory=list)
    recommended_tasks: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: str = "draft"
    metadata: dict = Field(default_factory=dict)


class ModelInstallResult(BaseModel):
    """Result of model download/install operation."""

    resource_id: str
    provider: str
    model: str
    local_path: str | None
    status: str
    ready: bool
    message: str
    metadata: dict = Field(default_factory=dict)