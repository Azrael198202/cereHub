from core.contracts.artifact import ArtifactModel


def resolve_or_build_tools(required_tools: list[str]) -> tuple[list[dict], list[ArtifactModel]]:
    resolved: list[dict] = []
    artifacts: list[ArtifactModel] = []

    for tool_name in required_tools:
        resolution_result = "prebuilt" if tool_name == "reminder_tool" else "generated_code"
        resolved.append({"tool_name": tool_name, "resolution_result": resolution_result})
        artifacts.append(
            ArtifactModel(
                id=f"artifact_{tool_name}",
                type="tool",
                source_intent="create_agent",
                source_task="resolve_tools",
                version="1.0.0",
                status="registered",
                runnable=True,
                registered_at="runtime",
            )
        )
    return resolved, artifacts
