from __future__ import annotations

from core.brain.helpers import new_id
from core.brain.workflows.planner.step_builder import create_step
from core.contracts.intent import IntentModel
from core.contracts.workflow import WorkflowModel


async def build_template_workflow(intent: IntentModel) -> WorkflowModel:
    """Build a deterministic fallback workflow from intent."""

    if intent.intent_type == "agent_creation_intent":
        steps = [
            create_step(new_id("task"), 1, "collect_requirements", "requirement_collection", "Collect requirements for the new assistant.", "planner_agent"),
            create_step(new_id("task"), 2, "generate_blueprint", "blueprint_generation", "Generate blueprint for the new assistant.", "blueprint_designer_agent"),
            create_step(new_id("task"), 3, "resolve_tools", "tool_resolution", "Resolve tools for the blueprint.", "tool_manager_agent"),
            create_step(new_id("task"), 4, "register_artifacts", "artifact_registration", "Register blueprint and tool artifacts.", "artifact_manager_agent"),
        ]
        return WorkflowModel(
            workflow_id=new_id("wf"),
            workflow_type="agent_creation",
            source_intent_id=intent.intent_id,
            name="create_agent_workflow",
            status="draft",
            version="1.0.0",
            goal="Create and register a new assistant capability.",
            steps=steps,
            final_validation_rule={
                "type": "intent_fulfillment_validation",
                "required_outcomes": intent.expected_outcome,
            },
        )

    steps = [
        create_step(new_id("task"), 1, "analyze_request", "intent_analysis", "Analyze the request.", "planner_agent"),
        create_step(new_id("task"), 2, "generate_response", "custom_task", "Generate a final response.", "response_agent"),
    ]
    return WorkflowModel(
        workflow_id=new_id("wf"),
        workflow_type="business_execution",
        source_intent_id=intent.intent_id,
        name="normal_request_workflow",
        status="draft",
        version="1.0.0",
        goal="Handle a normal request and return a response.",
        steps=steps,
        final_validation_rule={
            "type": "intent_fulfillment_validation",
            "required_outcomes": intent.expected_outcome,
        },
    )
