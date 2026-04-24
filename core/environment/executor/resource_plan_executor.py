from __future__ import annotations

import os

from core.contracts.install_plan import CommandResult, InstallPlan
from core.runtime.command_runner import CommandRunner


class ResourcePlanExecutor:
    """Executes resource preparation plans through a permission gate."""

    def __init__(self) -> None:
        self.runner = CommandRunner()

    def execute(self, plan: InstallPlan) -> list[CommandResult]:
        """Execute commands only when policy allows risky operations."""

        allow_install = os.getenv("NESTHUB_ALLOW_INSTALL", "false").lower() == "true"
        results: list[CommandResult] = []

        for command in plan.commands:
            if command.risky and not allow_install:
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

            results.append(self.runner.run(command))

        return results
