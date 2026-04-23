
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class RuntimeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    session_id: str = "default"
    locale: str = "en"


class RuntimeResponse(BaseModel):
    status: Literal["success", "clarification", "failed"]
    reply: str
    intent: dict[str, Any]
    workflow: dict[str, Any]
    traces: list[dict[str, Any]]
    artifacts: list[dict[str, Any]] = Field(default_factory=list)


class IntentModel(BaseModel):
    intent_id: str
    intent_type: Literal["normal_intent", "agent_creation_intent"]
    name: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    expected_outcome: list[str] = Field(default_factory=list)
    requires_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    source_text: str


class TaskModel(BaseModel):
    task_id: str
    step_index: int
    name: str
    task_type: str
    objective: str
    assigned_agent_type: str
    required_tools: list[str] = Field(default_factory=list)
    input_schema: str
    output_schema: str
    depends_on: list[str] = Field(default_factory=list)
    status: str = "pending"


class WorkflowModel(BaseModel):
    workflow_id: str
    workflow_type: Literal["business_execution", "agent_creation"]
    source_intent_id: str
    name: str
    status: str = "draft"
    version: str = "1.0.0"
    goal: str
    steps: list[TaskModel]
    final_validation_rule: dict[str, Any]


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
