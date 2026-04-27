from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    """Load a JSON file relative to project root."""
    full_path = BASE_DIR / path
    return json.loads(full_path.read_text(encoding="utf-8"))


MODELS = load_json("core/config/models.json")


SETTINGS = {
    "ollama": {
        "api_base": os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
    },
    "litellm": {
        "base_url": "http://localhost:4000/v1",
        "api_key": "anything"
    },
    "runtime": {
        "model_timeout": int(os.getenv("MODEL_TIMEOUT", "30")),
        "model_retry": int(os.getenv("MODEL_RETRY", "1")),
        "allow_install": os.getenv("NESTHUB_ALLOW_INSTALL", "false").lower() == "true",
    },
}