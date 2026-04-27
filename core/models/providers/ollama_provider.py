from __future__ import annotations

import json
import re
from typing import Any

from litellm import acompletion

from core.models.providers.base import BaseModelProvider


class OllamaProvider(BaseModelProvider):
    """LiteLLM-backed Ollama provider."""

    def __init__(self, api_base: str = "http://localhost:11434") -> None:
        self.api_base = api_base

    async def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Call Ollama through LiteLLM and parse JSON output."""

        response = await acompletion(
            model=f"ollama/{model}",
            api_base=self.api_base,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty model response")

        return self._parse_json(content)

    def _parse_json(self, content: str) -> dict[str, Any]:
        """Parse a JSON object from model output."""

        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end + 1])

        raise ValueError(f"Model output is not valid JSON: {content[:300]}")
