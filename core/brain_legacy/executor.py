"""Execute step by step and write trace/artifact."""

from datetime import datetime, timezone
from typing import Any

from core.contracts.models import IntentModel, TraceModel, WorkflowModel
from core.brain_legacy.tool_builder import resolve_or_build_tools


def execute_workflow(
    intent: IntentModel, workflow: WorkflowModel
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Execute the workflow and return the final reply, trace list, and artifact list."""
    traces: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    reply = ""
    blueprint_id = None

    # Iterate through each task step in the workflow and simulate execution
    for step in workflow.steps:
        started = datetime.now(timezone.utc).isoformat()
        task_output: dict[str, Any] = {}
        tool_calls: list[dict[str, Any]] = []

        if step.name == "collect_requirements":
            # Collect requirements from the intent metadata
            task_output = {
                "agent_role": intent.entities.get("agent_role", "generic_assistant"),
                "required_tools": intent.entities.get("required_tools", []),
            }

        elif step.name == "generate_blueprint":
            # Generate a blueprint ID and register blueprint artifact details
            blueprint_id = f"bp_{intent.entities.get('agent_role', 'generic_assistant')}_v1"
            task_output = {
                "blueprint_id": blueprint_id,
                "agent_role": intent.entities.get("agent_role", "generic_assistant"),
                "capabilities": intent.entities.get("required_capabilities", []),
            }
            artifacts.append({
                "id": blueprint_id,
                "type": "blueprint",
                "source_intent": intent.name,
                "source_task": step.name,
                "version": "1.0.0",
                "status": "registered",
                "runnable": True,
                "registered_at": "runtime",
            })

        elif step.name == "resolve_tools":
            # Resolve or construct required tools for the blueprint
            resolved, tool_artifacts = resolve_or_build_tools(intent.entities.get("required_tools", []))
            task_output = {"resolved_tools": resolved}
            artifacts.extend(tool_artifacts)
            tool_calls = [
                {
                    "tool_name": item["tool_name"],
                    "status": "success",
                    "input_ref": None,
                    "output_ref": None,
                    "error_reason": None,
                }
                for item in resolved
            ]

        elif step.name == "register_artifacts":
            # Register artifact metadata for later use
            task_output = {"registered_artifact_ids": [a["id"] for a in artifacts]}

        elif step.name == "analyze_request":
            # Analyze a normal request by normalizing the input text
            task_output = {"normalized_request": intent.source_text.strip()}

        elif step.name == "generate_response":
            # Generate a simple response for normal requests
            reply = f"Handled as normal intent: {intent.name}"
            task_output = {"reply": reply}

        # Append trace information for the executed step
        traces.append(
            TraceModel(
                trace_id=f"trace_{workflow.workflow_id}_{step.step_index}",
                workflow_id=workflow.workflow_id,
                task_id=step.task_id,
                step_index=step.step_index,
                intent_id=intent.intent_id,
                agent_id=f"agent_{step.assigned_agent_type}",
                agent_type=step.assigned_agent_type,
                blueprint_id=blueprint_id,
                tool_calls=tool_calls,
                task_input={"intent_name": intent.name},
                task_output=task_output,
                validation_result={
                    "step_goal_met": True,
                    "schema_valid": True,
                    "intent_alignment": True,
                    "messages": [],
                },
                retry_count=0,
                fallback_used=False,
                status="success",
                error_reason=None,
                started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),
            ).model_dump()
        )

    # If this was an agent creation workflow, produce a creation summary reply
    if intent.intent_type == "agent_creation_intent":
        role = intent.entities.get("agent_role", "generic_assistant").replace("_", " ").title()
        reply = f"{role} Assistant has been created in starter runtime form."

    return reply, traces, artifacts
