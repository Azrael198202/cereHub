from core.brain.planning.intent_classifier import classify_intent
from core.brain.validation.schema_validator import validate_against
from core.brain.workflows.executor.service import execute_workflow
from core.brain.workflows.planner.service import build_workflow
from core.contracts.request import RuntimeRequest
from core.contracts.response import RuntimeResponse


def handle_request(request: RuntimeRequest) -> RuntimeResponse:
    """
    Main orchestration entry for the core brain.
    """
    intent = classify_intent(request.text)
    validate_against("intent.schema.json", intent.model_dump())

    workflow = build_workflow(intent)
    validate_against("workflow.schema.json", workflow.model_dump())

    reply, traces, artifacts, validation = execute_workflow(intent, workflow)

    return RuntimeResponse(
        status="success",
        reply=reply,
        intent=intent.model_dump(),
        workflow=workflow.model_dump(),
        traces=traces,
        artifacts=artifacts,
        validation=validation,
    )
