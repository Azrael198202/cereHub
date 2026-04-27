'''Abstract base class for model providers.'''

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseModelProvider(ABC):
    """Abstract interface for model providers."""

    @abstractmethod
    async def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Return a JSON object produced by the model."""
        raise NotImplementedError
