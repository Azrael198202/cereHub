from __future__ import annotations

import subprocess

from core.contracts.install_plan import CommandResult, InstallCommand


class CommandRunner:
    """Runs commands with a small safety boundary."""

    def run(self, command: InstallCommand, timeout: int = 300) -> CommandResult:
        """Run a command and return a structured result."""

        if command.requires_shell:
            proc = subprocess.run(
                " ".join(command.command),
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            proc = subprocess.run(
                command.command,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        return CommandResult(
            name=command.name,
            command=command.command,
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            skipped=False,
        )
