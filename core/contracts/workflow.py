from typing import Any, Literal
from pydantic import BaseModel, Field

from core.contracts.task import TaskModel


class WorkflowModel(BaseModel):
    workflow_id: str
    workflow_type: Literal["business_execution", "agent_creation"]
    source_intent_id: str
    name: str
    status: str = "draft"
    version: str = "1.0.0"
    goal: str
    steps: list[TaskModel] = Field(default_factory=list)
    final_validation_rule: dict[str, Any] = Field(default_factory=dict)
