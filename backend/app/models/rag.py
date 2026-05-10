from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    section_id: str
    text: str
    page: Optional[int]
    embedding: Optional[List[float]] = None
    source_label: Optional[str] = None


class RAGResult(BaseModel):
    text: str
    score: float
    source_document: str
    section_title: str
    page: Optional[int]
    citations: List[str] = []
