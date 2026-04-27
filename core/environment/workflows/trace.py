from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


class WorkflowTraceRecorder:
    """Records structured traces for resource preparation workflows."""

    def __init__(self) -> None:
        self.records: list[dict] = []

    def record(
        self,
        workflow_id: str,
        task_id: str,
        step_index: int,
        name: str,
        status: str,
        task_input: dict,
        task_output: dict,
        error_reason: Optional[str] = None,
    ) -> dict:
        """Append a trace record."""

        now = datetime.now(timezone.utc).isoformat()
        record = {
            "trace_id": f"trace_{workflow_id}_{step_index}",
            "workflow_id": workflow_id,
            "task_id": task_id,
            "step_index": step_index,
            "name": name,
            "agent_type": "environment_manager_agent",
            "task_input": task_input,
            "task_output": task_output,
            "validation_result": {
                "step_goal_met": status == "success",
                "schema_valid": True,
                "messages": [],
            },
            "retry_count": 0,
            "fallback_used": False,
            "status": status,
            "error_reason": error_reason,
            "started_at": now,
            "finished_at": now,
        }
        self.records.append(record)
        return record
