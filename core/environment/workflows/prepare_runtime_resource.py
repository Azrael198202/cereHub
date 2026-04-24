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
from core.environment.workflows.trace import WorkflowTraceRecorder


WORKFLOW_ID = "wf_prepare_runtime_resource"


class PrepareRuntimeResourceWorkflow:
    """Generic controlled workflow for preparing any runtime resource."""

    def __init__(self) -> None:
        self.detector = ResourceDetector()
        self.planner = ResourcePlanBuilder()
        self.executor = ResourcePlanExecutor()
        self.validator = ResourceValidator()
        self.registry = RuntimeResourceRegistry()
        self.trace = WorkflowTraceRecorder()

    def run(self, resource: RuntimeResource) -> ResourcePreparationResult:
        """Run the resource preparation workflow."""

        detected = self.detector.detect(resource)
        self.trace.record(
            WORKFLOW_ID,
            "task_detect_resource",
            1,
            "detect_resource",
            "success",
            resource.model_dump(),
            detected,
        )

        plan = self.planner.build_plan(resource, detected)
        self.trace.record(
            WORKFLOW_ID,
            "task_generate_preparation_plan",
            2,
            "generate_preparation_plan",
            "success",
            detected,
            plan.model_dump(),
        )

        permission_output = {
            "allowed_by_policy": True,
            "note": "Risky commands are still blocked unless NESTHUB_ALLOW_INSTALL=true.",
        }
        self.trace.record(
            WORKFLOW_ID,
            "task_permission_gate",
            3,
            "permission_gate",
            "success",
            plan.model_dump(),
            permission_output,
        )

        command_results = self.executor.execute(plan)
        self.trace.record(
            WORKFLOW_ID,
            "task_execute_preparation_plan",
            4,
            "execute_preparation_plan",
            "success",
            plan.model_dump(),
            {"command_results": [r.model_dump() for r in command_results]},
        )

        validation = self.validator.validate(resource)
        self.trace.record(
            WORKFLOW_ID,
            "task_verify_resource",
            5,
            "verify_resource",
            "success" if validation["resource_ready"] else "failed",
            resource.model_dump(),
            validation,
            None if validation["resource_ready"] else "Resource is not ready.",
        )

        capability = self.registry.register(
            resource.resource_id,
            {
                "resource": resource.model_dump(),
                "ready": validation["resource_ready"],
                "validation": validation,
            },
        )
        self.trace.record(
            WORKFLOW_ID,
            "task_register_resource",
            6,
            "register_resource",
            "success",
            validation,
            {"capability_registered": True, "capability": capability},
        )

        return ResourcePreparationResult(
            resource_id=resource.resource_id,
            resource_name=resource.name,
            ready=validation["resource_ready"],
            detected=detected,
            plan=plan.model_dump(),
            command_results=[r.model_dump() for r in command_results],
            validation=validation,
            capability=capability,
            traces=self.trace.records,
        )


def load_resource(path: str) -> RuntimeResource:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RuntimeResource(**payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource", required=True, help="Path to runtime resource JSON file.")
    args = parser.parse_args()

    resource = load_resource(args.resource)
    result = PrepareRuntimeResourceWorkflow().run(resource)
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
