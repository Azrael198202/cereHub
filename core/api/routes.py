"""API route definitions for the Cerehub core service."""

from fastapi import APIRouter

from core.brain.orchestration.service import handle_request
from core.contracts.models import RuntimeRequest

# Create an API router instance for route registration
router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Return a simple health check response."""
    return {"status": "ok", "service": "cerehub-core"}


@router.post("/chat")
async def chat(request: RuntimeRequest) -> dict:
    """Accept a runtime chat request and return the runtime response."""
    response = handle_request(request)
    return response.model_dump()
