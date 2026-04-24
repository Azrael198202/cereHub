from __future__ import annotations

import re

from core.brain.helpers import new_id
from core.brain.validation.schema_validator import validate_against
from core.contracts.intent import IntentModel
from core.contracts.request import RuntimeRequest
from core.models.router import ModelRouter
from core.runtime.logger import get_logger

logger = get_logger(__name__)
router = ModelRouter()


def classify_and_validate_intent(request: RuntimeRequest) -> IntentModel:
    """Classify intent by model, normalize only structural fields, validate schema, and return IntentModel."""
    try:
        logger.info(f"[intent] input={request.text}")

        raw = router.complete_intent(request.text)
        logger.info(f"[intent] raw={raw}")

        normalized = normalize_intent_payload(raw, request.text)
        logger.info(f"[intent] normalized={normalized}")

        validate_against("intent.schema.json", normalized)
        return IntentModel(**normalized)
    except Exception as e:
        logger.exception("[intent] failed")
        raise


def normalize_intent_payload(raw: dict, source_text: str) -> dict:
    """Normalize model output to satisfy intent.schema.json.

    Important:
    - Do not infer business intent here.
    - Do not use domain keywords such as schedule, expense, calendar, etc.
    - The model must decide intent_type, name, entities, and expected_outcome.
    - This function only fixes schema shape and safe defaults.
    """

    payload = dict(raw)

    payload.setdefault("intent_id", new_id("intent"))
    payload.setdefault("description", "")
    payload.setdefault("entities", {})
    payload.setdefault("constraints", {})
    payload.setdefault("requires_clarification", False)
    payload.setdefault("clarification_questions", [])
    payload.setdefault("source_text", source_text)

    payload["name"] = normalize_schema_name(
        payload.get("name")
        or payload.get("intent_name")
        or "general_query"
    )

    payload["intent_type"] = normalize_intent_type(payload.get("intent_type"))

    payload["expected_outcome"] = normalize_expected_outcome(
        payload.get("expected_outcome"),
        payload["intent_type"],
    )

    if payload["intent_type"] == "agent_creation_intent":
        entities = payload.setdefault("entities", {})
        entities.setdefault("agent_role", "generic_assistant")

    payload["confidence"] = float(payload.get("confidence", 0.7))
    payload["description"] = str(payload["description"])
    payload["source_text"] = str(payload["source_text"])

    return payload


def normalize_schema_name(value: object) -> str:
    """Convert a model-generated name into schema-safe snake_case.

    Schema requires: ^[a-z][a-z0-9_]*$
    Example:
      "Create schedule assistant for family"
      -> "create_schedule_assistant_for_family"
    """

    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")

    if not text:
        text = "general_query"

    if not re.match(r"^[a-z]", text):
        text = f"intent_{text}"

    return text


def normalize_intent_type(value: object) -> str:
    """Normalize intent_type only to supported enum values.

    This is not business inference. Unsupported or missing values fall back
    to normal_intent so schema validation can proceed safely.
    """

    intent_type = str(value or "").strip()

    if intent_type in {"normal_intent", "agent_creation_intent"}:
        return intent_type

    return "normal_intent"


def default_expected_outcome(intent_type: str) -> list[str]:
    """Return generic default outcomes without domain-specific assumptions."""

    if intent_type == "agent_creation_intent":
        return [
            "blueprint_created",
            "creation_workflow_created",
            "agent_registered",
        ]

    return ["response_generated"]

def normalize_expected_outcome(value: object, intent_type: str) -> list[str]:
    """Normalize expected_outcome to non-empty string array."""

    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = []

    normalized = [
        normalize_schema_name(item)
        for item in items
        if str(item).strip()
    ]

    if normalized:
        return normalized

    return default_expected_outcome(intent_type)