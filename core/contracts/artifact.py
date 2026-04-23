from pydantic import BaseModel


class ArtifactModel(BaseModel):
    id: str
    type: str
    source_intent: str
    source_task: str
    version: str
    status: str
    runnable: bool
    registered_at: str
