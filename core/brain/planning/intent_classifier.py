from core.brain.helpers import new_id
from core.contracts.intent import IntentModel


AGENT_KEYWORDS = [
    "create assistant",
    "create agent",
    "schedule assistant",
    "create tool",
    "calendar tool",
]


def classify_intent(text: str) -> IntentModel:
    lowered = text.lower()
    is_creation = any(keyword in lowered for keyword in AGENT_KEYWORDS)

    if is_creation:
        role = "generic_assistant"
        required_tools: list[str] = []
        if "schedule" in lowered or "calendar" in lowered:
            role = "schedule_manager"
            required_tools.append("calendar_tool")
        if "reminder" in lowered:
            required_tools.append("reminder_tool")

        return IntentModel(
            intent_id=new_id("intent"),
            intent_type="agent_creation_intent",
            name="create_agent",
            description="Create a new runtime capability.",
            confidence=0.92,
            entities={
                "agent_role": role,
                "required_tools": required_tools,
                "required_capabilities": ["create_event", "update_event", "query_event"],
            },
            constraints={"runtime_mode": "dynamic_creation"},
            expected_outcome=["blueprint_created", "creation_workflow_created", "agent_registered"],
            source_text=text,
        )

    return IntentModel(
        intent_id=new_id("intent"),
        intent_type="normal_intent",
        name="manage_schedule",
        description="Handle a normal request.",
        confidence=0.88,
        entities={"raw_text": text},
        constraints={},
        expected_outcome=["response_generated"],
        source_text=text,
    )
