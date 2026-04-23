from typing import Any, Literal
from pydantic import BaseModel, Field


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
