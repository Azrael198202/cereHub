from __future__ import annotations

from copy import deepcopy

from core.brain.helpers import new_id
from core.brain.workflows.planner.step_builder import create_step
from core.contracts.intent import IntentModel


ALLOWED_TASK_TYPES = {
    "requirement_collection",
    "entity_resolution",
    "intent_analysis",
    "route_selection",
    "blueprint_generation",
    "workflow_generation",
    "tool_resolution",
    "spec_generation",
    "code_generation",
    "calendar_action",
    "artifact_registration",
    "agent_instantiation",
    "validation",
    "custom_task",
    "capability_detection",
    "resource_resolution",
    "environment_planning",
    "permission_gate",
    "environment_installation",
    "dependency_installation",
    "model_preparation",
    "tool_preparation",
    "runtime_validation",
    "capability_registration",
}

TASK_TYPE_ALIASES = {
    "generate_response": "validation",
    "response_generation": "validation",
    "final_response": "validation",
    "confirm_response": "validation",
    "confirmation": "validation",
    "tool_resolution_validation": "validation",
    "blueprint_validation": "validation",
    "artifact_registration_validation": "validation",
}

ALLOWED_VALIDATION_TYPES = {
    "schema_validation",
    "step_output_validation",
    "intent_fulfillment_validation",
    "custom_validation",
}


def _safe_str(value, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _normalize_name(value, default: str) -> str:
    name = _safe_str(value, default)
    name = name.lower().replace("-", "_").replace(" ", "_")

    cleaned = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            cleaned.append(ch)

    name = "".join(cleaned).strip("_")

    if not name:
        name = default

    if not name[0].isalpha() or not name[0].islower():
        name = f"step_{name}"

    return name


def _normalize_task_type(value) -> str:
    task_type = _safe_str(value, "custom_task")
    task_type = TASK_TYPE_ALIASES.get(task_type, task_type)

    if task_type not in ALLOWED_TASK_TYPES:
        return "custom_task"

    return task_type


def _normalize_retry_policy(value) -> dict:
    if not isinstance(value, dict):
        value = {}

    max_retries = value.get("max_retries", 2)
    if not isinstance(max_retries, int) or max_retries < 0:
        max_retries = 2

    fallback_allowed = value.get("fallback_allowed", True)
    if not isinstance(fallback_allowed, bool):
        fallback_allowed = True

    return {
        "max_retries": max_retries,
        "fallback_allowed": fallback_allowed,
    }


def _normalize_validation_rule(value) -> dict:
    if not isinstance(value, dict):
        value = {}

    rule_type = value.get("type", "schema_validation")

    if rule_type not in ALLOWED_VALIDATION_TYPES:
        rule_type = "custom_validation"

    normalized = dict(value)
    normalized["type"] = rule_type

    return normalized


def _normalize_string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item) for item in value if item is not None and str(item).strip()]


def _normalize_schema_ref(value, default: str) -> str:
    ''' Normalize schema reference to ensure it ends with _input or _output.'''
    ref = _safe_str(value, default)
    if isinstance(value, str) and value.strip():
        return value.strip()

    return default


def create_step(
    *,
    task_id: str,
    step_index: int,
    name: str,
    task_type: str,
    objective: str,
    assigned_agent_type: str,
) -> dict:
    return {
        "task_id": task_id,
        "step_index": step_index,
        "name": name,
        "task_type": task_type,
        "objective": objective,
        "assigned_agent_type": assigned_agent_type,
        "assigned_agent_id": None,
        "required_tools": [],
        "input_schema": f"{name}_input",
        "output_schema": f"{name}_output",
        "depends_on": [],
        "retry_policy": {
            "max_retries": 2,
            "fallback_allowed": True,
        },
        "validation_rule": {
            "type": "schema_validation",
        },
        "status": "pending",
        "notes": "",
    }


def normalize_workflow_payload(payload: dict, intent: IntentModel) -> dict:
    """Normalize model-generated workflow JSON so it satisfies workflow.schema.json."""

    workflow = deepcopy(payload) if isinstance(payload, dict) else {}

    is_agent_creation = intent.intent_type == "agent_creation_intent"

    workflow["workflow_id"] = _safe_str(workflow.get("workflow_id"), new_id("wf"))
    workflow["workflow_type"] = _safe_str(
        workflow.get("workflow_type"),
        "agent_creation" if is_agent_creation else "business_execution",
    )

    if workflow["workflow_type"] not in {
        "business_execution",
        "environment_preparation",
        "runtime_resource_preparation",
        "agent_creation",
    }:
        workflow["workflow_type"] = "agent_creation" if is_agent_creation else "business_execution"

    workflow["source_intent_id"] = _safe_str(
        workflow.get("source_intent_id"),
        intent.intent_id,
    )

    workflow["name"] = _normalize_name(
        workflow.get("name"),
        "create_agent_workflow" if is_agent_creation else "normal_request_workflow",
    )

    workflow["status"] = _safe_str(workflow.get("status"), "draft")
    if workflow["status"] not in {
        "draft",
        "registered",
        "active",
        "paused",
        "completed",
        "failed",
        "archived",
    }:
        workflow["status"] = "draft"

    workflow["version"] = _safe_str(workflow.get("version"), "1.0.0")
    workflow["goal"] = _safe_str(
        workflow.get("goal"),
        getattr(intent, "description", None) or "Handle user intent.",
    )

    expected_outcome = getattr(intent, "expected_outcome", None)
    if not isinstance(expected_outcome, list) or not expected_outcome:
        expected_outcome = ["intent_is_fulfilled"]

    final_validation_rule = workflow.get("final_validation_rule")
    if not isinstance(final_validation_rule, dict):
        final_validation_rule = {}

    final_type = final_validation_rule.get("type", "intent_fulfillment_validation")
    if final_type not in {"intent_fulfillment_validation", "custom_validation"}:
        final_type = "intent_fulfillment_validation"

    final_validation_rule["type"] = final_type

    if not isinstance(final_validation_rule.get("required_outcomes"), list) or not final_validation_rule.get("required_outcomes"):
        final_validation_rule["required_outcomes"] = expected_outcome

    workflow["final_validation_rule"] = final_validation_rule

    normalized_steps = []

    raw_steps = workflow.get("steps")
    if not isinstance(raw_steps, list):
        raw_steps = []

    for index, step in enumerate(raw_steps, start=1):
        if not isinstance(step, dict):
            continue

        name = _normalize_name(step.get("name"), f"step_{index}")

        base = create_step(
            task_id=_safe_str(step.get("task_id"), new_id("task")),
            step_index=index,
            name=name,
            task_type=_normalize_task_type(step.get("task_type")),
            objective=_safe_str(step.get("objective"), f"Execute {name}."),
            assigned_agent_type=_safe_str(
                step.get("assigned_agent_type"),
                "planner_agent",
            ),
        )

        base.update({k: v for k, v in step.items() if v is not None})

        # ---- Force correction: prevent LLM-generated values from overriding schema-compliant values. ----

        base["task_id"] = _safe_str(base.get("task_id"), new_id("task"))
        base["step_index"] = index
        base["name"] = name
        base["task_type"] = _normalize_task_type(base.get("task_type"))
        base["objective"] = _safe_str(base.get("objective"), f"Execute {name}.")
        base["assigned_agent_type"] = _safe_str(
            base.get("assigned_agent_type"),
            "planner_agent",
        )

        assigned_agent_id = base.get("assigned_agent_id")
        if assigned_agent_id is not None:
            assigned_agent_id = _safe_str(assigned_agent_id, "")
            base["assigned_agent_id"] = assigned_agent_id or None
        else:
            base["assigned_agent_id"] = None

        base["required_tools"] = _normalize_string_list(base.get("required_tools"))
        base["input_schema"] = _normalize_schema_ref(
            base.get("input_schema"),
            f"{name}_input",
        )
        base["output_schema"] = _normalize_schema_ref(
            base.get("output_schema"),
            f"{name}_output",
        )
        base["depends_on"] = _normalize_string_list(base.get("depends_on"))
        base["retry_policy"] = _normalize_retry_policy(base.get("retry_policy"))
        base["validation_rule"] = _normalize_validation_rule(base.get("validation_rule"))

        status = _safe_str(base.get("status"), "pending")
        if status not in {
            "pending",
            "running",
            "success",
            "failed",
            "skipped",
            "blocked",
        }:
            status = "pending"

        base["status"] = status
        base["notes"] = str(base.get("notes") or "")

        normalized_steps.append(base)

    if not normalized_steps:
        normalized_steps.append(
            create_step(
                task_id=new_id("task"),
                step_index=1,
                name="handle_request",
                task_type="custom_task",
                objective=workflow["goal"],
                assigned_agent_type="planner_agent",
            )
        )

    workflow["steps"] = normalized_steps

    # workflow.schema.json additionalProperties=false，clear out any extra keys that the model might have generated
    allowed_workflow_keys = {
        "workflow_id",
        "workflow_type",
        "source_intent_id",
        "name",
        "status",
        "version",
        "goal",
        "steps",
        "final_validation_rule",
        "metadata",
    }

    return {k: v for k, v in workflow.items() if k in allowed_workflow_keys}
