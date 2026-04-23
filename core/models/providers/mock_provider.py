''' Mock provider for testing and development. '''
from __future__ import annotations

from typing import Any

from core.models.providers.base import BaseModelProvider


class MockProvider(BaseModelProvider):
    """Fallback mock provider for development and failure cases."""

    def complete_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """
        Return a deterministic mock intent result.
        """

        text = user_prompt.lower()

        # 👉 简单规则 fallback（你原来的 classifier 升级版）
        if "create" in text or "创建" in text:
            intent_type = "agent_creation"
        elif "calendar" in text or "日程" in text:
            intent_type = "schedule_management"
        elif "expense" in text or "消费" in text:
            intent_type = "expense_tracking"
        else:
            intent_type = "general_query"

        return {
            "intent_type": intent_type,
            "entities": {},
            "expected_outcome": "Handle user request",
            "confidence": 0.6,  # 👉 故意低一点，方便触发 fallback逻辑测试
            "requires_clarification": False,
        }