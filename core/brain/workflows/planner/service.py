"""Planner service that builds workflows from detected intents."""

from core.brain.validation.schema_validator import validate_against
from core.brain.workflows.planner.model_planner import ModelWorkflowPlanner
from core.brain.workflows.planner.template_planner import build_template_workflow
from core.contracts.intent import IntentModel
from core.contracts.workflow import WorkflowModel


async def build_workflow(intent: IntentModel) -> WorkflowModel:
    """Build a workflow using model planner with deterministic fallback."""

    try:
        workflow = await ModelWorkflowPlanner().build(intent)
        await validate_against("workflow.schema.json", workflow.model_dump())
        return workflow
    except Exception as exc:
        print("workflow model planner failed, fallback to template planner:", exc)

    ''' template planner is a deterministic fallback that ensures we can always generate a workflow, even if the model planner fails.'''
    workflow = await build_template_workflow(intent)
    await validate_against("workflow.schema.json", workflow.model_dump())
    return workflow
