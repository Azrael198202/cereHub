from typing import Any
from pydantic import BaseModel, Field


class BlueprintModel(BaseModel):
    blueprint_id: str
    blueprint_type: str = "agent_blueprint"
    version: str = "1.0.0"
    agent_role: str
    display_name: str
    description: str
    supported_intents: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    tool_requirements: list[dict[str, Any]] = Field(default_factory=list)
    input_contract: dict[str, Any] = Field(default_factory=dict)
    output_contract: dict[str, Any] = Field(default_factory=dict)
    execution_policies: dict[str, Any] = Field(default_factory=dict)
    collaboration_rules: dict[str, Any] = Field(default_factory=dict)
    status: str = "draft"
