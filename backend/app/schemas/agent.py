from typing import Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    success: bool
    message: Optional[str] = None


class AgentPlanRequest(BaseModel):
    prompt: str
    persona_id: Optional[str] = None
