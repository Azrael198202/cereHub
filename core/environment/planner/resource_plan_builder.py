from __future__ import annotations

import platform

from core.contracts.install_plan import InstallCommand, InstallPlan
from core.contracts.runtime_resource import RuntimeResource


class ResourcePlanBuilder:
    """Builds generic installation or preparation plans for runtime resources."""

    def build_plan(self, resource: RuntimeResource, detection: dict, *, force: bool = False) -> InstallPlan:
        """Build a preparation plan based on resource metadata and detection result."""

        if detection.get("installed") and not force:
            return InstallPlan(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                resource_name=resource.name,
                plan_required=False,
                reason="Resource already appears to be available.",
                commands=[],
            )

        commands: list[InstallCommand] = []

        if resource.install_commands:
            commands.extend(
                InstallCommand(
                    name=f"install_{resource.name}_{index + 1}",
                    command=command,
                    requires_shell=self._requires_shell(command),
                    risky=self._is_risky(command),
                    reason="Command provided by resource configuration.",
                )
                for index, command in enumerate(resource.install_commands)
            )
        else:
            commands.extend(self._build_default_commands(resource))

        return InstallPlan(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            resource_name=resource.name,
            plan_required=bool(commands),
            reason="Resource is missing or forced preparation was requested.",
            commands=commands,
        )

    def _build_default_commands(self, resource: RuntimeResource) -> list[InstallCommand]:
        if resource.resource_type == "local_model" and resource.provider == "ollama":
            return [
                InstallCommand(
                    name=f"ollama_pull_{resource.name}",
                    command=["ollama", "pull", resource.name],
                    risky=False,
                    reason="Pull local model through Ollama.",
                )
            ]

        if resource.resource_type == "python_package":
            return [
                InstallCommand(
                    name=f"pip_install_{resource.name}",
                    command=["python", "-m", "pip", "install", resource.name],
                    risky=False,
                    reason="Install Python package using pip.",
                )
            ]

        if resource.resource_type in ["cli_tool", "software", "system_dependency"]:
            return self._system_package_hint(resource)

        return []

    def _system_package_hint(self, resource: RuntimeResource) -> list[InstallCommand]:
        system = platform.system().lower()

        if resource.name == "ollama" and system == "linux":
            return [
                InstallCommand(
                    name="install_ollama_linux",
                    command=["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"],
                    requires_shell=True,
                    risky=True,
                    reason="Install Ollama on Linux using official install script.",
                )
            ]

        return [
            InstallCommand(
                name=f"install_{resource.name}_manual_hint",
                command=["echo", f"Install {resource.name} manually or define install_commands."],
                risky=False,
                reason="Generic install hint.",
            )
        ]

    def _requires_shell(self, command: list[str]) -> bool:
        return any(token in command for token in ["|", "&&", ";", ">", "<"])

    def _is_risky(self, command: list[str]) -> bool:
        risky_tokens = ["sudo", "curl", "apt", "yum", "dnf", "brew", "npm"]
        return any(token in command for token in risky_tokens)