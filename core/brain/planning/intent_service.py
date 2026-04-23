'''Service for classifying user intents and validating them against a schema.'''
from __future__ import annotations

from core.contracts.intent import IntentModel
from core.contracts.request import RuntimeRequest
from core.brain.validation.schema_validator import validate_against
from core.models.router import ModelRouter

router = ModelRouter()

def classify_and_validate_intent(request: RuntimeRequest) -> IntentModel:
    # In a real implementation, this would call out to an LLM or other model to classify the intent based on the request text and possibly other metadata.
    raw = router.complete_intent(request.text)
    validate_against("intent.schema.json", raw)
    return IntentModel(**raw)