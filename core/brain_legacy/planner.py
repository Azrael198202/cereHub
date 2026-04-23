"""Planner module that assembles workflows based on detected intents."""

from core.brain.helpers import new_id
from core.contracts.models import IntentModel, TaskModel, WorkflowModel


def build_workflow(intent: IntentModel) -> WorkflowModel:
    """Build a workflow model based on the provided intent."""
    if intent.intent_type == "agent_creation_intent":
        # Create a workflow for agent creation
        steps = [
            TaskModel(
                task_id=new_id("task"),
                step_index=1,
                name="collect_requirements",
                task_type="requirement_collection",
                objective="Collect requirements for the new assistant.",
                assigned_agent_type="planner_agent",
                input_schema="agent_requirement_input",
                output_schema="agent_requirement_output",
            ),
            TaskModel(
                task_id=new_id("task"),
                step_index=2,
                name="generate_blueprint",
                task_type="blueprint_generation",
                objective="Generate blueprint for the new assistant.",
                assigned_agent_type="blueprint_designer_agent",
                input_schema="blueprint_generation_input",
                output_schema="blueprint_output",
            ),
            TaskModel(
                task_id=new_id("task"),
                step_index=3,
                name="resolve_tools",
                task_type="tool_resolution",
                objective="Resolve tools for the blueprint.",
                assigned_agent_type="tool_manager_agent",
                input_schema="tool_resolution_input",
                output_schema="tool_resolution_output",
            ),
            TaskModel(
                task_id=new_id("task"),
                step_index=4,
                name="register_artifacts",
                task_type="artifact_registration",
                objective="Register blueprint and tool artifacts.",
                assigned_agent_type="artifact_manager_agent",
                input_schema="artifact_registration_input",
                output_schema="artifact_registration_output",
            ),
        ]
        return WorkflowModel(
            workflow_id=new_id("wf"),
            workflow_type="agent_creation",
            source_intent_id=intent.intent_id,
            name="create_agent_workflow",
            goal="Create and register a new assistant capability.",
            steps=steps,
            final_validation_rule={
                "type": "intent_fulfillment_validation",
                "required_outcomes": intent.expected_outcome,
            },
        )

    # Create a standard workflow for normal business execution requests
    steps = [
        TaskModel(
            task_id=new_id("task"),
            step_index=1,
            name="analyze_request",
            task_type="intent_analysis",
            objective="Analyze the request.",
            assigned_agent_type="planner_agent",
            input_schema="normal_request_input",
            output_schema="normal_request_output",
        ),
        TaskModel(
            task_id=new_id("task"),
            step_index=2,
            name="generate_response",
            task_type="response_generation",
            objective="Generate a final response.",
            assigned_agent_type="response_agent",
            input_schema="response_input",
            output_schema="response_output",
        ),
    ]
    return WorkflowModel(
        workflow_id=new_id("wf"),
        workflow_type="business_execution",
        source_intent_id=intent.intent_id,
        name="normal_request_workflow",
        goal="Handle a normal request and return a response.",
        steps=steps,
        final_validation_rule={
            "type": "intent_fulfillment_validation",
            "required_outcomes": intent.expected_outcome,
        },
    )
