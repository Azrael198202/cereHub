from __future__ import annotations

import json
import re
from typing import Any

from openai import APIConnectionError
from openai import AsyncOpenAI

from core.models.providers.base import BaseModelProvider


class LiteLLMProvider(BaseModelProvider):
    """LiteLLM Proxy provider."""

    def __init__(
        self,
        api_base: str | None = None,
        base_url: str | None = None,
        api_key: str = "anything",
    ) -> None:
        self.api_base = api_base or base_url or "http://localhost:4000/v1"
        self.api_key = api_key
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )

    async def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                model=model,  # local-intent / cloud-chat 这种别名可以放这里
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except APIConnectionError as exc:
            raise RuntimeError(
                f"LiteLLM proxy is not reachable at {self.api_base}. "
                "Start the VS Code task 'Start LiteLLM Proxy' or run "
                "'.venv/bin/litellm --config core/config/litellm.config.yaml --port 4000'."
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty model response")

        return self._parse_json(content)

    def _parse_json(self, content: str) -> dict[str, Any]:
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
