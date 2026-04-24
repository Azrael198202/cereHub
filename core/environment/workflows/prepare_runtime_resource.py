from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.contracts.install_plan import ResourcePreparationResult
from core.contracts.runtime_resource import RuntimeResource
from core.environment.detectors.resource_detector import ResourceDetector
from core.environment.executor.resource_plan_executor import ResourcePlanExecutor
from core.environment.planner.resource_plan_builder import ResourcePlanBuilder
from core.environment.registry.resource_registry import RuntimeResourceRegistry
from core.environment.validators.resource_validator import ResourceValidator
from core.brain.trace.recorder import build_trace
from core.brain.trace.store import TraceStore


WORKFLOW_ID = "wf_prepare_runtime_resource"
ENV_INTENT_ID = "intent_runtime_resource_preparation"


class PrepareRuntimeResourceWorkflow:
    """Generic controlled workflow for preparing any runtime resource."""

    def __init__(self) -> None:
        self.detector = ResourceDetector()
        self.planner = ResourcePlanBuilder()
        self.executor = ResourcePlanExecutor()
        self.validator = ResourceValidator()
        self.registry = RuntimeResourceRegistry()
        self.trace_store = TraceStore()

    def run(self, resource: RuntimeResource, *, force: bool = False) -> ResourcePreparationResult:
        """Run the resource preparation workflow."""

        traces = []

        detected = self.detector.detect(resource)
        traces.append(self._trace(1, "task_detect_resource", "detect_resource", resource.model_dump(), detected, "success"))

        plan = self.planner.build_plan(resource, detected, force=force)
        traces.append(self._trace(2, "task_generate_preparation_plan", "generate_preparation_plan", detected, plan.model_dump(), "success"))

        permission_output = {
            "allowed_by_policy": True,
            "note": "Risky commands are still blocked unless NESTHUB_ALLOW_INSTALL=true.",
            "force": force,
        }
        traces.append(self._trace(3, "task_permission_gate", "permission_gate", plan.model_dump(), permission_output, "success"))

        command_results = self.executor.execute(plan)
        command_output = {"command_results": [r.model_dump() for r in command_results]}
        traces.append(self._trace(4, "task_execute_preparation_plan", "execute_preparation_plan", plan.model_dump(), command_output, "success"))

        validation = self.validator.validate(resource)
        traces.append(
            self._trace(
                5,
                "task_verify_resource",
                "verify_resource",
                resource.model_dump(),
                validation,
                "success" if validation["resource_ready"] else "failed",
                None if validation["resource_ready"] else "Resource is not ready.",
            )
        )

        capability = self.registry.register(
            resource.resource_id,
            {
                "resource": resource.model_dump(),
                "ready": validation["resource_ready"],
                "validation": validation,
            },
        )
        traces.append(self._trace(6, "task_register_resource", "register_resource", validation, {"capability_registered": True, "capability": capability}, "success"))

        self.trace_store.append_many(traces)

        return ResourcePreparationResult(
            resource_id=resource.resource_id,
            resource_name=resource.name,
            ready=validation["resource_ready"],
            detected=detected,
            plan=plan.model_dump(),
            command_results=[r.model_dump() for r in command_results],
            validation=validation,
            capability=capability,
            traces=[t.model_dump() for t in traces],
        )

    def _trace(
        self,
        step_index: int,
        task_id: str,
        name: str,
        task_input: dict,
        task_output: dict,
        status: str,
        error_reason: str | None = None,
    ):
        return build_trace(
            workflow_id=WORKFLOW_ID,
            task_id=task_id,
            step_index=step_index,
            intent_id=ENV_INTENT_ID,
            agent_type="environment_manager_agent",
            blueprint_id=None,
            task_input={"name": name, **task_input},
            task_output=task_output,
            tool_calls=[],
            validation_result={
                "schema_valid": True,
                "step_goal_met": status == "success",
                "messages": [],
            },
            status=status,
            error_reason=error_reason,
        )


def load_resource(path: str) -> RuntimeResource:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RuntimeResource(**payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    resource = load_resource(args.resource)
    result = PrepareRuntimeResourceWorkflow().run(resource, force=args.force)
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()