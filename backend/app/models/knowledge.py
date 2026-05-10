from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class KnowledgePointType(str):
    concept = "概念"
    theorem = "定理"
    method = "方法"
    phenomenon = "现象"


class KnowledgePoint(BaseModel):
    id: str
    title: str
    type: KnowledgePointType
    description: str
    source_document_id: str
    section_id: str
    tags: List[str] = []
    frequency: int = 1


class KnowledgeNode(BaseModel):
    id: str
    label: str
    category: str
    description: Optional[str]
    source: str
    frequency: int = 1
    metadata: dict = {}


class KnowledgeEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    weight: Optional[float] = None


class KnowledgeGraph(BaseModel):
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]
    metadata: dict = {}
