from typing import Any, Literal
from pydantic import BaseModel, Field


class RuntimeResponse(BaseModel):
    status: Literal["success", "clarification", "failed"]
    reply: str
    intent: dict[str, Any]
    workflow: dict[str, Any]
    traces: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
