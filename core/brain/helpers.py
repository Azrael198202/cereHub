"""A general function for generating IDs can be retained."""

import uuid


def new_id(prefix: str) -> str:
    """Generate a short unique identifier using the given prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
