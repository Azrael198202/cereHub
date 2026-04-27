'''Orchestration service that ties together intent classification, workflow planning, validation, and execution.'''
from core.brain.planning.intent_service import classify_and_validate_intent

# Deprecated: legacy starter implementation
#from core.brain.planning.intent_classifier import classify_intent

from core.brain.validation.schema_validator import validate_against
from core.brain.workflows.executor.service import execute_workflow
from core.brain.workflows.planner.service import build_workflow
from core.contracts.request import RuntimeRequest
from core.contracts.response import RuntimeResponse
from core.runtime.logger import get_logger

logger = get_logger(__name__)

async def handle_request(request: RuntimeRequest) -> RuntimeResponse:
    """
    Main orchestration entry for the core brain.
    """
    try:
        logger.info("[orchestration] start")

        intent = await classify_and_validate_intent(request)
        logger.info(f"[orchestration] intent={intent.name}")

        workflow = await build_workflow(intent)
        await validate_against("workflow.schema.json", workflow.model_dump())
        logger.info(f"[orchestration] workflow={workflow.name}")

        reply, traces, artifacts, validation = await execute_workflow(intent, workflow)

        return RuntimeResponse(
            status="success",
            reply=reply,
            intent=intent.model_dump(),
            workflow=workflow.model_dump(),
            traces=traces,
            artifacts=artifacts,
            validation=validation,
        )
    except Exception:
        logger.exception("[orchestration] failed")
        raise
