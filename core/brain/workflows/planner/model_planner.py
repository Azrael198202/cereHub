from __future__ import annotations

from core.brain.validation.schema_validator import validate_against
from core.brain.workflows.planner.normalizer import normalize_workflow_payload
from core.brain.workflows.planner.prompt import build_workflow_prompt
from core.contracts.intent import IntentModel
from core.contracts.workflow import WorkflowModel
from core.models.router import ModelRouter


class ModelWorkflowPlanner:
    """Generates workflow plans using configured workflow models."""

    def __init__(self) -> None:
        self.router = ModelRouter()

    def build(self, intent: IntentModel) -> WorkflowModel:
        """Generate, normalize, validate, and return workflow."""

        system_prompt, user_prompt = build_workflow_prompt(intent)

        raw = self.router.complete_json(
            task_type="workflow",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        normalized = normalize_workflow_payload(raw, intent)
        validate_against("workflow.schema.json", normalized)

        return WorkflowModel(**normalized)
