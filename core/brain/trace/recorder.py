from datetime import datetime, timezone
from typing import Any, Optional

from core.contracts.trace import TraceModel


def build_trace(
    workflow_id: str,
    task_id: str,
    step_index: int,
    intent_id: str,
    agent_type: str,
    blueprint_id: Optional[str],
    task_input: dict[str, Any],
    task_output: dict[str, Any],
    tool_calls: list[dict[str, Any]],
    validation_result: dict[str, Any],
) -> TraceModel:
    started = datetime.now(timezone.utc).isoformat()
    return TraceModel(
        trace_id=f"trace_{workflow_id}_{step_index}",
        workflow_id=workflow_id,
        task_id=task_id,
        step_index=step_index,
        intent_id=intent_id,
        agent_id=f"agent_{agent_type}",
        agent_type=agent_type,
        blueprint_id=blueprint_id,
        tool_calls=tool_calls,
        task_input=task_input,
        task_output=task_output,
        validation_result=validation_result,
        retry_count=0,
        fallback_used=False,
        status="success",
        error_reason=None,
        started_at=started,
        finished_at=datetime.now(timezone.utc).isoformat(),
    )
