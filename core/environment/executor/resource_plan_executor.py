from __future__ import annotations

import os
import subprocess
from typing import Optional

from core.contracts.install_plan import CommandResult, InstallPlan
from core.runtime.progress import progress_store


class ResourcePlanExecutor:
    """Executes resource preparation plans through a permission gate with visible progress."""

    def execute(self, plan: InstallPlan) -> list[CommandResult]:
        """Execute commands only when policy allows risky operations."""

        allow_install = os.getenv("NESTHUB_ALLOW_INSTALL", "false").lower() == "true"
        results: list[CommandResult] = []

        progress_store.emit(
            "resource_plan",
            f"Preparing resource: {plan.resource_name}",
            status="running",
            operation_id=plan.resource_id,
            payload=plan.model_dump(),
        )

        total = max(len(plan.commands), 1)

        for index, command in enumerate(plan.commands, start=1):
            if command.risky and not allow_install:
                progress_store.emit(
                    "command_skipped",
                    f"Skipped risky command: {command.name}",
                    status="skipped",
                    operation_id=plan.resource_id,
                    progress=index / total,
                    payload=command.model_dump(),
                )
                results.append(
                    CommandResult(
                        name=command.name,
                        command=command.command,
                        return_code=0,
                        stdout="Skipped risky command. Set NESTHUB_ALLOW_INSTALL=true to allow.",
                        stderr="",
                        skipped=True,
                    )
                )
                continue

            progress_store.emit(
                "command_start",
                f"Running command: {command.name}",
                status="running",
                operation_id=plan.resource_id,
                progress=(index - 1) / total,
                payload=command.model_dump(),
            )

            result = self._run_streaming(command, operation_id=plan.resource_id)
            results.append(result)

            progress_store.emit(
                "command_done",
                f"Command finished: {command.name} rc={result.return_code}",
                status="success" if result.return_code == 0 else "failed",
                operation_id=plan.resource_id,
                progress=index / total,
                payload=result.model_dump(),
            )

        progress_store.emit(
            "resource_plan_done",
            f"Finished preparing resource: {plan.resource_name}",
            status="success",
            operation_id=plan.resource_id,
            progress=1.0,
            payload={"return_codes": [item.return_code for item in results]},
        )

        return results

    def _run_streaming(self, command, operation_id: Optional[str] = None) -> CommandResult:
        """Run a command and stream stdout/stderr into progress events."""

        if command.requires_shell:
            popen_args = {
                "args": " ".join(command.command),
                "shell": True,
            }
        else:
            popen_args = {
                "args": command.command,
                "shell": False,
            }

        proc = subprocess.Popen(
            **popen_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        output_lines: list[str] = []

        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip()
            output_lines.append(line)
            if line:
                progress_store.emit(
                    "command_output",
                    line,
                    status="running",
                    operation_id=operation_id,
                    payload={"command": command.command, "command_name": command.name},
                )

        return_code = proc.wait()

        return CommandResult(
            name=command.name,
            command=command.command,
            return_code=return_code,
            stdout="\n".join(output_lines),
            stderr="",
            skipped=False,
        )
