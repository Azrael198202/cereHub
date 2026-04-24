from __future__ import annotations

from core.contracts.runtime_resource import RuntimeResource
from core.environment.detectors.resource_detector import ResourceDetector


class ResourceValidator:
    """Validates runtime resource availability after preparation."""

    def __init__(self) -> None:
        self.detector = ResourceDetector()

    def validate(self, resource: RuntimeResource) -> dict:
        """Return validation result for the runtime resource."""

        detection = self.detector.detect(resource)

        if resource.resource_type == "local_model":
            ready = bool(detection.get("installed"))
        else:
            ready = bool(detection.get("installed"))
            if resource.healthcheck_url:
                ready = ready and bool(detection.get("api_ready"))

        return {
            "resource_ready": ready,
            "resource_id": resource.resource_id,
            "resource_type": resource.resource_type,
            "name": resource.name,
            "provider": resource.provider,
            "detection": detection,
        }