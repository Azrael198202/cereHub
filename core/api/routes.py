"""API route definitions for the Cerehub core service."""

from fastapi import APIRouter

from core.brain.orchestration.service import handle_request
from core.contracts.models import RuntimeRequest
from core.runtime.progress import progress_store


# Create an API router instance for route registration
router = APIRouter()

"""Define API routes for the Cerehub core service."""
@router.get("/health")
async def health() -> dict:
    """Return a simple health check response."""
    return {"status": "ok", "service": "cerehub-core"}

"""Define an API route for handling runtime chat requests."""
@router.post("/chat")
async def chat(request: RuntimeRequest) -> dict:
    """Accept a runtime chat request and return the runtime response."""
    response = handle_request(request)
    return response.model_dump()

"""Define API routes for retrieving runtime progress events."""
@router.get("/progress")
async def list_progress(limit: int = 200) -> dict:
    """Return recent runtime progress events."""

    return {"events": progress_store.list_events(limit=limit)}

"""Define an API route for retrieving the latest runtime progress event."""
@router.get("/progress/latest")
async def latest_progress() -> dict:
    """Return the latest runtime progress event."""

    return {"latest": progress_store.latest()}

