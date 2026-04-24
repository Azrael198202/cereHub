'''Defines the RuntimeResource model, which represents a resource required by a workflow, tool, model, or assistant at runtime.'''
from __future__ import annotations

from typing import Literal
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
]


class RuntimeResource(BaseModel):
    """A runtime resource required by a workflow, tool, model, or assistant."""

    resource_id: str
    resource_type: ResourceType
    name: str
    provider: str | None = None
    version: str | None = None
    required: bool = True
    install_strategy: list[str] = Field(default_factory=list)
    install_commands: list[list[str]] = Field(default_factory=list)
    verification_command: list[str] | None = None
    healthcheck_url: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    status: str = "unknown"
    metadata: dict = Field(default_factory=dict)