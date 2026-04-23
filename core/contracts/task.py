from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskModel(BaseModel):
    task_id: str
    step_index: int
    name: str
    task_type: str
    objective: str
    assigned_agent_type: str
    assigned_agent_id: Optional[str] = None
    required_tools: list[str] = Field(default_factory=list)
    input_schema: str
    output_schema: str
    depends_on: list[str] = Field(default_factory=list)
    retry_policy: dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 0, "fallback_allowed": False}
    )
    validation_rule: dict[str, Any] = Field(
        default_factory=lambda: {"type": "schema_validation"}
    )
    status: str = "pending"
    notes: str = ""
