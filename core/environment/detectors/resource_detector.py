from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request

from core.contracts.runtime_resource import RuntimeResource


class ResourceDetector:
    """Detects whether a generic runtime resource is available."""

    def detect(self, resource: RuntimeResource) -> dict:
        """Return a generic detection result for the resource."""

        if resource.healthcheck_url:
            health = self._check_health_url(resource.healthcheck_url)
        else:
            health = {"api_ready": None, "details": {}}

        command_available = None
        command_result = None

        if resource.verification_command:
            command_result = self._run_verification_command(resource.verification_command)
            command_available = command_result["return_code"] == 0
        elif resource.resource_type in ["cli_tool", "software"]:
            command_available = shutil.which(resource.name) is not None

        if resource.resource_type == "local_model":
            # Local model readiness usually depends on provider health plus model listing.
            installed = bool(health.get("api_ready"))
        elif command_available is not None:
            installed = command_available
        else:
            installed = bool(health.get("api_ready"))

        return {
            "resource_id": resource.resource_id,
            "resource_type": resource.resource_type,
            "name": resource.name,
            "provider": resource.provider,
            "installed": installed,
            "api_ready": health.get("api_ready"),
            "command_available": command_available,
            "command_result": command_result,
            "details": health.get("details", {}),
        }

    def _run_verification_command(self, command: list[str]) -> dict:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=10)
            return {
                "return_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except Exception as exc:
            return {
                "return_code": -1,
                "stdout": "",
                "stderr": str(exc),
            }

    def _check_health_url(self, url: str) -> dict:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    payload = json.loads(raw)
                except Exception:
                    payload = {"raw": raw}
                return {"api_ready": True, "details": payload}
        except Exception as exc:
            return {"api_ready": False, "details": {"error": str(exc)}}
