from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional


class AgentPersona(BaseModel):
    id: str
    name: str
    role: str
    style: str
    taunt_level: int = 0
    fixed_traits: List[str] = []


class DialogueTurn(BaseModel):
    speaker: str
    message: str
    timestamp: Optional[str] = None
    metadata: dict = {}


class EvaluationResult(BaseModel):
    score: float
    feedback: str
    weak_points: List[str] = []
