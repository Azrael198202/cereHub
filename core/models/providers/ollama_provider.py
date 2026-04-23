''' Ollama provider implementation using LiteLLM.'''
from __future__ import annotations

import json
from typing import Any

from litellm import completion

from core.models.providers.base import BaseModelProvider


class OllamaProvider(BaseModelProvider):
    """LiteLLM-backed Ollama provider."""

    def __init__(self, api_base: str = "http://localhost:11434") -> None:
        self.api_base = api_base

    def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        response = completion(
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
        return json.loads(content)