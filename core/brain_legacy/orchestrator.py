"""Connect the classifier, planner, and executor together."""

from core.brain_legacy.classifier import classify_intent
from core.brain_legacy.executor import execute_workflow
from core.brain_legacy.planner import build_workflow
from core.contracts.models import RuntimeRequest, RuntimeResponse


def run(request: RuntimeRequest) -> RuntimeResponse:
    intent = classify_intent(request.text)
    workflow = build_workflow(intent)
    reply, traces, artifacts = execute_workflow(intent, workflow)
    return RuntimeResponse(
        status="success",
        reply=reply,
        intent=intent.model_dump(),
        workflow=workflow.model_dump(),
        traces=traces,
        artifacts=artifacts,
    )
