from __future__ import annotations

from typing import Any

from core.contracts.trace import TraceModel


class TraceEvaluator:
    """Evaluates trace records and workflow outcomes."""

    def evaluate_step(self, trace: TraceModel) -> dict[str, Any]:
        """Evaluate one trace record."""

        validation = trace.validation_result or {}

        schema_valid = bool(validation.get("schema_valid", False))
        step_goal_met = bool(validation.get("step_goal_met", False))
        status_success = trace.status == "success"
        no_error = trace.error_reason is None

        passed = schema_valid and step_goal_met and status_success and no_error

        messages: list[str] = []
        if not schema_valid:
            messages.append("Schema validation failed.")
        if not step_goal_met:
            messages.append("Step goal was not met.")
        if not status_success:
            messages.append(f"Trace status is {trace.status}.")
        if trace.error_reason:
            messages.append(trace.error_reason)

        return {
            "trace_id": trace.trace_id,
            "workflow_id": trace.workflow_id,
            "task_id": trace.task_id,
            "passed": passed,
            "schema_valid": schema_valid,
            "step_goal_met": step_goal_met,
            "status_success": status_success,
            "no_error": no_error,
            "messages": messages,
        }

    def evaluate_workflow(self, traces: list[TraceModel]) -> dict[str, Any]:
        """Evaluate all traces for one workflow."""

        step_results = [self.evaluate_step(trace) for trace in traces]
        passed = all(item["passed"] for item in step_results)

        return {
            "passed": passed,
            "total_steps": len(step_results),
            "failed_steps": [item for item in step_results if not item["passed"]],
            "step_results": step_results,
        }

    def evaluate_intent_outcome(
        self,
        traces: list[TraceModel],
        required_outcomes: list[str],
    ) -> dict[str, Any]:
        """Evaluate whether final task outputs include required outcomes."""

        observed: set[str] = set()

        for trace in traces:
            self._collect_observed_values(trace.task_output, observed)

        missing = [outcome for outcome in required_outcomes if outcome not in observed]

        return {
            "passed": not missing,
            "required_outcomes": required_outcomes,
            "observed_outcomes": sorted(observed),
            "missing_outcomes": missing,
        }

    def _collect_observed_values(self, value: Any, observed: set[str]) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                observed.add(str(key))
                self._collect_observed_values(item, observed)
            return

        if isinstance(value, list):
            for item in value:
                self._collect_observed_values(item, observed)
            return

        if value is not None:
            observed.add(str(value))
