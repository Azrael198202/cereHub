'''Defines the RuntimeResource model, which represents a resource required by a workflow, tool, model, or assistant at runtime.'''
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


ResourceType = Literal[
    "software",
    "python_package",
    "node_package",
    "cli_tool",
    "local_model",
    "external_model",
    "browser_runtime",
    "system_dependency",
    "tool_code",
    "huggingface_model",
    "gguf_model",
    "transformers_model"
]


class RuntimeResource(BaseModel):
    """A runtime resource required by a workflow, tool, model, or assistant."""

    resource_id: str
    resource_type: ResourceType
    name: str
    provider: Optional[str] = None
    version: Optional[str] = None
    required: bool = True
    install_strategy: list[str] = Field(default_factory=list)
    install_commands: list[list[str]] = Field(default_factory=list)
    verification_command: Optional[list[str]] = None
    healthcheck_url: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    status: str = "unknown"
    metadata: dict = Field(default_factory=dict)
