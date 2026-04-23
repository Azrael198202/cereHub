"""Do intent categorization."""

from core.brain.helpers import new_id
from core.contracts.models import IntentModel

# Classifies the user's input text into an IntentModel.
# Determines if the intent is to create a new agent/assistant or a normal request.
def classify_intent(text: str) -> IntentModel:
    # Convert input text to lowercase for easier keyword matching
    lowered = text.lower()

    # Check if the text contains any keywords indicating agent/assistant creation
    is_creation = any(
        key in lowered
        for key in [
            "create assistant",
            "create agent",
            "schedule assistant",
            "create tool",
            "calendar tool",
        ]
    )

    if is_creation:
        # Default role and required tools
        role = "generic_assistant"
        required_tools = []
        # If scheduling or calendar is mentioned, set role and add tool
        if "schedule" in lowered or "calendar" in lowered:
            role = "schedule_manager"
            required_tools.append("calendar_tool")
        # If reminder is mentioned, add reminder tool
        if "reminder" in lowered:
            required_tools.append("reminder_tool")

        # Return an IntentModel for agent creation
        return IntentModel(
            intent_id=new_id("intent"),  # Generate unique intent ID
            intent_type="agent_creation_intent",  # Mark as agent creation
            name="create_agent",
            description="Create a new runtime capability.",
            confidence=0.92,  # High confidence for matched keywords
            entities={
                "agent_role": role,
                "required_tools": required_tools,
                "required_capabilities": ["create_event", "update_event", "query_event"],
            },
            constraints={"runtime_mode": "dynamic_creation"},
            expected_outcome=["blueprint_created", "creation_workflow_created", "agent_registered"],
            source_text=text,
        )

    # If not agent creation, treat as a normal intent
    return IntentModel(
        intent_id=new_id("intent"),  # Generate unique intent ID
        intent_type="normal_intent",  # Mark as normal intent
        name="manage_schedule",
        description="Handle a normal request.",
        confidence=0.88,  # Slightly lower confidence
        entities={"raw_text": text},
        constraints={},
        expected_outcome=["response_generated"],
        source_text=text,
    )
