import json
import os
from pathlib import Path
from dotenv import load_dotenv

# load .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_json(path: str):
    with open(BASE_DIR / path, "r", encoding="utf-8") as f:
        return json.load(f)


MODELS = load_json("config/models.json")


SETTINGS = {
    "ollama": {
        "api_base": os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "api_base": os.getenv("OPENAI_API_BASE"),
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
    "runtime": {
        "timeout": int(os.getenv("MODEL_TIMEOUT", 10)),
        "retry": int(os.getenv("MODEL_RETRY", 2)),
    },
}