import json
from pathlib import Path

from jsonschema import validate
from core.runtime.logger import get_logger

logger = get_logger(__name__)

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def validate_against(schema_name: str, payload: dict) -> None:
    try:
        schema_path = SCHEMA_DIR / schema_name
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validate(instance=payload, schema=schema)
    except Exception:
        logger.exception(f"[schema] validation failed: {schema_name}")
        logger.error(f"[schema] payload={payload}")
        raise
