import json
from pathlib import Path

from jsonschema import validate


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def validate_against(schema_name: str, payload: dict) -> None:
    schema_path = SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate(instance=payload, schema=schema)
