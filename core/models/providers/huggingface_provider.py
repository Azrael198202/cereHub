from __future__ import annotations

import json
from typing import Any, Optional

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from core.models.providers.base import BaseModelProvider

"""Hugging Face Transformers provider."""
class HuggingFaceProvider(BaseModelProvider):
    """Local Hugging Face Transformers provider.

    Large models may require GPU, quantization, or sufficient memory.
    """

    def __init__(self, local_path: Optional[str] = None) -> None:
        self.local_path = local_path
        self._pipelines: dict[str, Any] = {}

    async def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Generate text and parse it as JSON."""

        pipe = self._get_pipeline(model)
        prompt = f"{system_prompt}\n\nUser:\n{user_prompt}\n\nJSON:"
        output = pipe(
            prompt,
            max_new_tokens=512,
            do_sample=temperature > 0,
            temperature=temperature,
        )

        text = output[0]["generated_text"]
        if text.startswith(prompt):
            text = text[len(prompt):].strip()

        return self._parse_json(text)

    async def _get_pipeline(self, model: str):
        key = self.local_path or model
        if key in self._pipelines:
            return self._pipelines[key]

        tokenizer = AutoTokenizer.from_pretrained(key, trust_remote_code=True)
        model_obj = AutoModelForCausalLM.from_pretrained(key, trust_remote_code=True)
        pipe = pipeline("text-generation", model=model_obj, tokenizer=tokenizer)
        self._pipelines[key] = pipe
        return pipe

    def _parse_json(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start:end + 1]
        return json.loads(cleaned)
