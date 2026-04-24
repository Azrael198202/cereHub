'''Structured models for controlled installation plans and results.'''
from __future__ import annotations

from pydantic import BaseModel, Field


class InstallCommand(BaseModel):
    """A single command in a controlled installation plan."""

    name: str
    command: list[str]
    requires_shell: bool = False
    risky: bool = False
    reason: str | None = None


class InstallPlan(BaseModel):
    """Controlled preparation plan for a runtime resource."""

    resource_id: str
    resource_type: str
    resource_name: str
    plan_required: bool
    reason: str
    commands: list[InstallCommand] = Field(default_factory=list)


class CommandResult(BaseModel):
    """Structured command execution result."""

    name: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    skipped: bool = False


class ResourcePreparationResult(BaseModel):
    """Final result of resource preparation workflow."""

    resource_id: str
    resource_name: str
    ready: bool
    detected: dict
    plan: dict
    command_results: list[dict]
    validation: dict
    capability: dict
    traces: list[dict]