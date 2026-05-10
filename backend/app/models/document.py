from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class DocumentFormat(str, Enum):
    pdf = "pdf"
    md = "md"
    txt = "txt"
    docx = "docx"


class DocumentSource(BaseModel):
    id: str
    name: str
    format: DocumentFormat
    path: Optional[str]
    metadata: dict = {}


class Section(BaseModel):
    id: str
    title: str
    chapter: Optional[str]
    order: int
    text: str
    page: Optional[int]


class DocumentStructure(BaseModel):
    source: DocumentSource
    sections: List[Section]
    raw_text: Optional[str] = None
