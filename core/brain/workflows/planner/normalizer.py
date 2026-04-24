from __future__ import annotations

from core.brain.helpers import new_id
from core.brain.workflows.planner.step_builder import create_step
from core.contracts.intent import IntentModel


def normalize_workflow_payload(payload: dict, intent: IntentModel) -> dict:
    """Normalize model-generated workflow JSON so it satisfies schema."""

    workflow = dict(payload)

    workflow.setdefault("workflow_id", new_id("wf"))
    workflow.setdefault("workflow_type", "agent_creation" if intent.intent_type == "agent_creation_intent" else "business_execution")
    workflow.setdefault("source_intent_id", intent.intent_id)
    workflow.setdefault("name", "create_agent_workflow" if intent.intent_type == "agent_creation_intent" else "normal_request_workflow")
    workflow.setdefault("status", "draft")
    workflow.setdefault("version", "1.0.0")
    workflow.setdefault("goal", intent.description or "Handle user intent.")
    workflow.setdefault(
        "final_validation_rule",
        {
            "type": "intent_fulfillment_validation",
            "required_outcomes": intent.expected_outcome,
        },
    )

    normalized_steps = []
    for index, step in enumerate(workflow.get("steps") or [], start=1):
        if not isinstance(step, dict):
            continue

        name = step.get("name") or f"step_{index}"
        base = create_step(
            task_id=step.get("task_id") or new_id("task"),
            step_index=int(step.get("step_index") or index),
            name=name,
            task_type=step.get("task_type") or "custom_task",
            objective=step.get("objective") or f"Execute {name}.",
            assigned_agent_type=step.get("assigned_agent_type") or "planner_agent",
        )

        base.update({k: v for k, v in step.items() if v is not None})

        base.setdefault("assigned_agent_id", None)
        base.setdefault("required_tools", [])
        base.setdefault("input_schema", f"{name}_input")
        base.setdefault("output_schema", f"{name}_output")
        base.setdefault("depends_on", [])
        base.setdefault("retry_policy", {"max_retries": 2, "fallback_allowed": True})
        base.setdefault("validation_rule", {"type": "schema_validation"})
        base.setdefault("status", "pending")
        base.setdefault("notes", "")

        if "max_retries" not in base["retry_policy"]:
            base["retry_policy"]["max_retries"] = 2
        if "fallback_allowed" not in base["retry_policy"]:
            base["retry_policy"]["fallback_allowed"] = True
        if "type" not in base["validation_rule"]:
            base["validation_rule"]["type"] = "schema_validation"

        normalized_steps.append(base)

    workflow["steps"] = normalized_steps

    return workflow
