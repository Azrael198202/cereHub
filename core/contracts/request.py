from pydantic import BaseModel, Field


class RuntimeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    session_id: str = "default"
    locale: str = "en"
