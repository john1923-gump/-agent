from typing import List, Optional
from pydantic import BaseModel
from app.models.knowledge import KnowledgeGraph, KnowledgeNode, KnowledgeEdge


class KnowledgeGraphResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    graph: KnowledgeGraph
