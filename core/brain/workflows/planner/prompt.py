from __future__ import annotations

import json

from core.contracts.intent import IntentModel


def build_workflow_prompt(intent: IntentModel) -> tuple[str, str]:
    """Build prompts for model-based workflow planning."""

    system_prompt = (
        "You are a workflow planner for NestHub.\n"
        "Return ONLY one valid JSON object. No markdown. No explanation.\n"
        "The JSON must match WorkflowModel and workflow.schema.json.\n"
        "Every step MUST include: task_id, step_index, name, task_type, objective, "
        "assigned_agent_type, assigned_agent_id, required_tools, input_schema, "
        "output_schema, depends_on, retry_policy, validation_rule, status, notes.\n"
        "retry_policy MUST include max_retries and fallback_allowed.\n"
        "validation_rule MUST include type.\n"
        "Use snake_case for names.\n"
        "Use workflow_type business_execution for normal_intent.\n"
        "Use workflow_type agent_creation for agent_creation_intent.\n"
        "Keep the workflow small and executable.\n"
        "Prefer existing executable step names: collect_requirements, generate_blueprint, "
        "resolve_tools, register_artifacts, analyze_request, generate_response.\n"
    )

    user_prompt = json.dumps(
        {
            "intent": intent.model_dump(),
            "allowed_workflow_types": [
                "business_execution",
                "agent_creation",
                "runtime_resource_preparation",
                "environment_preparation",
            ],
            "allowed_task_types": [
                "requirement_collection",
                "entity_resolution",
                "intent_analysis",
                "route_selection",
                "blueprint_generation",
                "workflow_generation",
                "tool_resolution",
                "spec_generation",
                "code_generation",
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
            ],
            "required_final_validation_rule": {
                "type": "intent_fulfillment_validation",
                "required_outcomes": intent.expected_outcome,
            },
        },
        ensure_ascii=False,
        indent=2,
    )

    return system_prompt, user_prompt
