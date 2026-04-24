"""Core entrypoint for the Cerehub service.

This module sets up the FastAPI application, mounts the UI asset directory,
and exposes a simple root endpoint for service discovery.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.api.routes import router as api_router
from core.runtime.logger import setup_logger

setup_logger()

# Create the FastAPI application instance with metadata
app = FastAPI(title="cerehub-core", version="0.1.0")

# Register the API router under the /api prefix
app.include_router(api_router, prefix="/api")

# Mount the static UI directories so /ui/app/ and /ui/box/ are served
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
app.mount("/static", StaticFiles(directory="core/static"), name="static")


@app.get("/")
async def root() -> dict:
    """Return basic service metadata for health and discovery."""
    return {
        "name": "cerehub",
        "service": "core",
        "status": "running",
        "ui": {
            "box": "/ui/box/",
            "app": "/ui/app/"
        }
    }
