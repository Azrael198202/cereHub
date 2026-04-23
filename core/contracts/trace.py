from typing import Any, Optional
from pydantic import BaseModel, Field


class TraceModel(BaseModel):
    trace_id: str
    workflow_id: str
    task_id: str
    step_index: int
    intent_id: str
    agent_id: str
    agent_type: str
    blueprint_id: Optional[str] = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    task_input: dict[str, Any] = Field(default_factory=dict)
    task_output: dict[str, Any] = Field(default_factory=dict)
    validation_result: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    fallback_used: bool = False
    status: str = "success"
    error_reason: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
