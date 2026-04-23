''' Router for handling model interactions, including intent classification. '''
''' This is a simplified example that demonstrates how to route requests to different model providers based on configuration.'''
from core.config.config_loader import MODELS, SETTINGS
from core.models.providers.ollama_provider import OllamaProvider
from core.models.providers.mock_provider import MockProvider

class ModelRouter:
    """Routes requests to different model providers based on configuration."""

    def __init__(self):
        # In a real implementation, this could be more dynamic and support loading different providers based on configuration.
        self.providers = {
            "ollama": OllamaProvider(
                api_base=SETTINGS["ollama"]["api_base"]
            ),
            "mock": MockProvider(),
        }

    def complete_intent(self, text: str):
        # This is a simplified routing logic. In a real implementation, 
        # you might have more complex logic to choose providers and models based on the request context, load, or other factors.  
        config = MODELS["intent"]

        primary = config["primary"]
        fallback = config.get("fallback")

        try:
            provider = self.providers[primary["provider"]]

            result = provider.complete_json(
                model=primary["model"],
                system_prompt=self._intent_prompt(),
                user_prompt=text,
                temperature=primary.get("temperature", 0.1),
            )

            if float(result.get("confidence", 0)) < 0.7:
                raise ValueError("Low confidence")

            return result

        except Exception as e:
            print("⚠️ primary model failed:", e)

            if fallback:
                provider = self.providers[fallback["provider"]]
                return provider.complete_json(
                    model=fallback["model"],
                    system_prompt=self._intent_prompt(),
                    user_prompt=text,
                )

            raise

    def _intent_prompt(self):
        # This prompt is designed to instruct the model to return a JSON object that conforms to the IntentModel schema. 
        # It emphasizes that the response should be strictly JSON without any additional text or formatting.
        return (
            "You are an intent classifier.\n"
            "Return ONLY a valid JSON object.\n"
            "No markdown, no explanation."
        )