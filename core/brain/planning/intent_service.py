from __future__ import annotations

from core.brain.helpers import new_id
from core.brain.validation.schema_validator import validate_against
from core.contracts.intent import IntentModel
from core.contracts.request import RuntimeRequest
from core.models.router import ModelRouter

router = ModelRouter()


def classify_and_validate_intent(request: RuntimeRequest) -> IntentModel:
    """Classify intent, normalize required fields, validate schema, and return IntentModel."""

    raw = router.complete_intent(request.text)
    normalized = normalize_intent_payload(raw, request.text)

    validate_against("intent.schema.json", normalized)
    return IntentModel(**normalized)


def normalize_intent_payload(raw: dict, source_text: str) -> dict:
    """Normalize model output to satisfy intent.schema.json."""

    payload = dict(raw)

    payload.setdefault("intent_id", new_id("intent"))
    payload.setdefault("intent_type", "normal_intent")
    payload.setdefault("name", "general_query")
    payload.setdefault("description", "")
    payload.setdefault("confidence", 0.7)
    payload.setdefault("entities", {})
    payload.setdefault("constraints", {})
    payload.setdefault("requires_clarification", False)
    payload.setdefault("clarification_questions", [])
    payload.setdefault("source_text", source_text)

    if "expected_outcome" not in payload or not payload["expected_outcome"]:
        if payload.get("intent_type") == "agent_creation_intent":
            payload["expected_outcome"] = [
                "blueprint_created",
                "creation_workflow_created",
                "agent_registered",
            ]
        else:
            payload["expected_outcome"] = ["response_generated"]

    if payload.get("intent_type") == "agent_creation_intent":
        payload.setdefault("entities", {})
        payload["entities"].setdefault("agent_role", "generic_assistant")

    return payload