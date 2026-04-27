'''
Service module for executing workflows based on intents. This module processes each step of the workflow, performs'''
from typing import Optional

from core.contracts.artifact import ArtifactModel
from core.contracts.blueprint import BlueprintModel
from core.contracts.intent import IntentModel
from core.contracts.workflow import WorkflowModel
from core.brain.artifacts.registry import register_artifacts
from core.brain.tools.resolver.service import resolve_or_build_tools
from core.brain.trace.recorder import build_trace
from core.brain.validation.schema_validator import validate_against

from core.runtime.logger import get_logger

logger = get_logger(__name__)

""" """
async def execute_workflow(intent: IntentModel, workflow: WorkflowModel) -> tuple[str, list[dict], list[dict], dict]:
    ''' execute workflow '''
    try:

        traces: list[dict] = []
        artifacts: list[ArtifactModel] = []
        reply = ""
        blueprint: Optional[BlueprintModel] = None

        await validate_against("intent.schema.json", intent.model_dump())
        await validate_against("workflow.schema.json", workflow.model_dump())

        for step in workflow.steps:
            task_output: dict = {}
            tool_calls: list[dict] = []

            if step.name == "collect_requirements":
                task_output = {"agent_role": intent.entities.get("agent_role", "generic_assistant"), "required_tools": intent.entities.get("required_tools", [])}

            elif step.name == "generate_blueprint":
                role = intent.entities.get("agent_role", "generic_assistant")
                blueprint = BlueprintModel(
                    blueprint_id=f"bp_{role}_v1",
                    agent_role=role,
                    display_name=role.replace("_", " ").title(),
                    description=f"Runtime assistant for {role}.",
                    supported_intents=["manage_schedule"] if "schedule" in role else ["generic_intent"],
                    capabilities=intent.entities.get("required_capabilities", []),
                    tool_requirements=[{"tool_name": tool_name, "required": True, "resolution_strategy": ["prebuilt", "generated_code"]} for tool_name in intent.entities.get("required_tools", [])],
                    input_contract={"schema_name": f"{role}_input"},
                    output_contract={"schema_name": f"{role}_output"},
                    execution_policies={"max_retries": 1, "trace_required": True, "step_validation_required": True, "fallback_agent_role": None},
                    collaboration_rules={"can_delegate_to": [], "can_receive_from": []},
                    status="registered",
                )
                await validate_against("blueprint.schema.json", blueprint.model_dump())
                task_output = blueprint.model_dump()
                artifacts.append(ArtifactModel(id=blueprint.blueprint_id, type="blueprint", source_intent=intent.name, source_task=step.name, version=blueprint.version, status="registered", runnable=True, registered_at="runtime"))

            elif step.name == "resolve_tools":
                resolved, tool_artifacts = await resolve_or_build_tools(intent.entities.get("required_tools", []))
                for item in resolved:
                    fake_tool_payload = {
                        "tool_name": item["tool_name"],
                        "tool_type": "runtime_tool",
                        "description": f"Resolved tool {item['tool_name']}.",
                        "input_contract": {"schema_name": f"{item['tool_name']}_input"},
                        "output_contract": {"schema_name": f"{item['tool_name']}_output"},
                        "implementation_type": item["resolution_result"],
                        "execution_mode": "local_runtime",
                        "dependencies": ["python"],
                        "entrypoint": None,
                        "status": "registered",
                        "version": "1.0.0",
                    }
                    await validate_against("tool.schema.json", fake_tool_payload)
                task_output = {"resolved_tools": resolved}
                artifacts.extend(tool_artifacts)
                tool_calls = [{"tool_name": item["tool_name"], "status": "success", "input_ref": None, "output_ref": None, "error_reason": None} for item in resolved]

            elif step.name == "register_artifacts":
                task_output = {"registered_artifact_ids": register_artifacts(artifacts)}

            elif step.name == "analyze_request":
                task_output = {"normalized_request": intent.source_text.strip()}

            elif step.name == "generate_response":
                reply = f"Handled as normal intent: {intent.name}"
                task_output = {"reply": reply}

            trace = await build_trace(
                workflow_id=workflow.workflow_id,
                task_id=step.task_id,
                step_index=step.step_index,
                intent_id=intent.intent_id,
                agent_type=step.assigned_agent_type,
                blueprint_id=blueprint.blueprint_id if blueprint else None,
                task_input={"intent_name": intent.name},
                task_output=task_output,
                tool_calls=tool_calls,
                validation_result={"step_goal_met": True, "schema_valid": True, "intent_alignment": True, "messages": []},
            )
            await validate_against("trace.schema.json", trace.model_dump())
            traces.append(trace.model_dump())

        if intent.intent_type == "agent_creation_intent":
            role = intent.entities.get("agent_role", "generic_assistant").replace("_", " ").title()
            reply = f"{role} Assistant has been created in phase 2 runtime form."

        validation = {"intent_level_success": True, "required_outcomes": intent.expected_outcome}
        return reply, traces, [artifact.model_dump() for artifact in artifacts], validation
    
    except Exception:
        logger.exception("[execute_workflow] failed")
        raise
