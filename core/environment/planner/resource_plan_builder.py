from __future__ import annotations

import platform

from core.contracts.install_plan import InstallCommand, InstallPlan
from core.contracts.runtime_resource import RuntimeResource


class ResourcePlanBuilder:
    """Builds generic installation or preparation plans for runtime resources."""

    def build_plan(self, resource: RuntimeResource, detection: dict) -> InstallPlan:
        """Build a preparation plan based on resource metadata and detection result."""

        commands: list[InstallCommand] = []

        if detection.get("installed"):
            return InstallPlan(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                resource_name=resource.name,
                plan_required=False,
                reason="Resource already appears to be available.",
                commands=[],
            )

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
            reason="Resource is missing or not verified.",
            commands=commands,
        )

    def _build_default_commands(self, resource: RuntimeResource) -> list[InstallCommand]:
        if resource.resource_type == "python_package":
            return [
                InstallCommand(
                    name=f"pip_install_{resource.name}",
                    command=["python", "-m", "pip", "install", resource.name],
                    risky=False,
                    reason="Install Python package using pip.",
                )
            ]

        if resource.resource_type == "node_package":
            return [
                InstallCommand(
                    name=f"npm_install_{resource.name}",
                    command=["npm", "install", "-g", resource.name],
                    risky=True,
                    reason="Install Node package globally.",
                )
            ]

        if resource.resource_type == "browser_runtime" and resource.provider == "playwright":
            return [
                InstallCommand(
                    name=f"playwright_install_{resource.name}",
                    command=["python", "-m", "playwright", "install", resource.name],
                    risky=False,
                    reason="Install Playwright browser runtime.",
                )
            ]

        if resource.resource_type == "local_model" and resource.provider == "ollama":
            # This prepares model only. Provider installation should be a separate software resource.
            return [
                InstallCommand(
                    name=f"ollama_pull_{resource.name}",
                    command=["ollama", "pull", resource.name],
                    risky=False,
                    reason="Pull local model through Ollama.",
                )
            ]

        if resource.resource_type in ["cli_tool", "software"]:
            return self._system_package_hint(resource)

        return []

    def _system_package_hint(self, resource: RuntimeResource) -> list[InstallCommand]:
        system = platform.system().lower()
        if system == "linux":
            return [
                InstallCommand(
                    name=f"install_{resource.name}_linux_hint",
                    command=["echo", f"Install {resource.name} using apt/yum/dnf according to your OS policy."],
                    risky=False,
                    reason="Generic Linux install hint. Avoid automatic package manager changes by default.",
                )
            ]
        if system == "darwin":
            return [
                InstallCommand(
                    name=f"install_{resource.name}_macos_hint",
                    command=["echo", f"Install {resource.name} using brew or official installer."],
                    risky=False,
                    reason="Generic macOS install hint.",
                )
            ]
        return [
            InstallCommand(
                name=f"install_{resource.name}_manual_hint",
                command=["echo", f"Manual installation required for {resource.name}."],
                risky=False,
                reason="Unsupported OS for automatic installation.",
            )
        ]

    def _requires_shell(self, command: list[str]) -> bool:
        return any(token in command for token in ["|", "&&", ";", ">", "<"])

    def _is_risky(self, command: list[str]) -> bool:
        risky_tokens = ["sudo", "curl", "apt", "yum", "dnf", "brew", "npm"]
        return any(token in command for token in risky_tokens)
