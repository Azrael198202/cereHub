from __future__ import annotations

from core.contracts.runtime_resource import RuntimeResource
from core.environment.detectors.resource_detector import ResourceDetector


class CapabilityResolver:
    """Resolves whether runtime resources are available or need preparation."""

    def __init__(self) -> None:
        self.detector = ResourceDetector()

    def resolve(self, resources: list[RuntimeResource]) -> list[dict]:
        """Return availability snapshots for all requested resources."""

        results = []
        for resource in resources:
            results.append(self.detector.detect(resource))
        return results