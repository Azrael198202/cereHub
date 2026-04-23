"""tool resolver."""

from typing import Any


def resolve_or_build_tools(required_tools: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    resolved: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    for tool_name in required_tools:
        if tool_name == "reminder_tool":
            resolved.append({
                "tool_name": tool_name,
                "resolution_result": "prebuilt",
            })
        else:
            resolved.append({
                "tool_name": tool_name,
                "resolution_result": "generated_code",
            })

        artifacts.append({
            "id": f"artifact_{tool_name}",
            "type": "tool",
            "source_intent": "create_agent",
            "source_task": "resolve_tools",
            "version": "1.0.0",
            "status": "registered",
            "runnable": True,
            "registered_at": "runtime",
        })

    return resolved, artifacts
