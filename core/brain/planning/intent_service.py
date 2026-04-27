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


async def classify_and_validate_intent(request: RuntimeRequest) -> IntentModel:
    """Classify intent by model, normalize only structural fields, validate schema, and return IntentModel."""
    try:
        logger.info(f"[intent] input={request.text}")

        raw = await router.complete_intent(request.text)
        logger.info(f"[intent] raw={raw}")

        normalized = await normalize_intent_payload(raw, request.text)
        logger.info(f"[intent] normalized={normalized}")

        await validate_against("intent.schema.json", normalized)
        return IntentModel(**normalized)
    except Exception as e:
        logger.exception("[intent] failed")
        raise


async def normalize_intent_payload(raw: dict, source_text: str) -> dict:
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

    payload["entities"] = await normalize_object_field(
        payload.get("entities"),
        fallback_key="value",
    )
    
    payload["constraints"] = await normalize_object_field(
        payload.get("constraints"),
        fallback_key="description",
    )
    payload.setdefault("requires_clarification", False)
    payload.setdefault("clarification_questions", [])
    payload.setdefault("source_text", source_text)

    payload["name"] = await normalize_schema_name(
        payload.get("name")
        or payload.get("intent_name")
        or "general_query"
    )

    payload["intent_type"] = await normalize_intent_type(payload.get("intent_type"))

    payload["expected_outcome"] = await normalize_expected_outcome(
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


async def normalize_schema_name(value: object) -> str:
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


async def normalize_intent_type(value: object) -> str:
    """Normalize intent_type only to supported enum values.

    This is not business inference. Unsupported or missing values fall back
    to normal_intent so schema validation can proceed safely.
    """

    intent_type = str(value or "").strip()

    if intent_type in {"normal_intent", "agent_creation_intent"}:
        return intent_type

    return "normal_intent"


async def default_expected_outcome(intent_type: str) -> list[str]:
    """Return generic default outcomes without domain-specific assumptions."""

    if intent_type == "agent_creation_intent":
        return [
            "blueprint_created",
            "creation_workflow_created",
            "agent_registered",
        ]

    return ["response_generated"]

async def normalize_expected_outcome(value: object, intent_type: str) -> list[str]:
    """Normalize expected_outcome to non-empty string array."""

    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = []

    normalized: list[str] = []
    for item in items:
        if not str(item).strip():
            continue
        normalized.append(await normalize_schema_name(item))

    if normalized:
        return normalized

    return await default_expected_outcome(intent_type)

async def normalize_object_field(value: object, fallback_key: str = "value") -> dict:
    """Normalize a model field to object/dict for schema compatibility."""

    if isinstance(value, dict):
        return value

    if value is None:
        return {}

    if isinstance(value, list):
        return {fallback_key: value}

    text = str(value).strip()
    if not text:
        return {}

    return {fallback_key: text}
