from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TextbookFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MD = "md"
    TXT = "txt"


class TextbookMeta(BaseModel):
    id: str
    filename: str
    format: TextbookFormat
    chapter_count: int = 0
    checksum: str = ""
    upload_time: str = ""


class Chapter(BaseModel):
    id: str = ""
    textbook_id: str = ""
    textbook_name: str = ""
    title: str = ""
    content: str = ""
    page_start: int = 0
    page_end: int = 0


class KnowledgeType(str, Enum):
    CONCEPT = "概念"
    THEOREM = "定理"
    METHOD = "方法"
    PHENOMENON = "现象"


class KnowledgePoint(BaseModel):
    id: str
    chapter_id: str
    textbook_id: str
    textbook_name: str
    chapter_title: str
    name: str
    description: str
    type: KnowledgeType
    confidence: float = 0.8
    relations: list[str] = []


class RelationType(str, Enum):
    PREREQUISITE = "prerequisite"
    PARALLEL = "parallel"
    CONTAINS = "contains"
    APPLIES_TO = "applies_to"


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    textbook_id: str = ""
    frequency: int = 1
    size: int = 20
    chapter_title: str = ""
    description: str = ""
    confidence: float = 0.8


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str = "关联"
    weight: float = 1.0


class Graph(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class IntegrationDecision(str, Enum):
    MERGE = "merge"
    KEEP = "keep"
    REMOVE = "remove"
    ENRICH = "enrich"


class IntegrationPair(BaseModel):
    kp_a: KnowledgePoint
    kp_b: KnowledgePoint
    similarity: float
    decision: IntegrationDecision
    reason: str
    merged_content: Optional[str] = None


class IntegrationResult(BaseModel):
    pairs: list[IntegrationPair] = []
    compression_ratio: float = 1.0
    original_count: int = 0
    final_count: int = 0
    original_text_chars: int = 0
    final_text_chars: int = 0
    merge_count: int = 0
    keep_count: int = 0
    remove_count: int = 0
    enrich_count: int = 0
    integrity_report: dict = {}
    coverage_report: dict = {}


class Chunk(BaseModel):
    id: str
    textbook_id: str
    textbook_name: str
    chapter_id: str
    chapter_title: str
    content: str
    page: int = 0


class QAReference(BaseModel):
    textbook: str = ""
    chapter: str = ""
    page: int = 0
    excerpt: str = ""


class QAResponse(BaseModel):
    answer: str
    references: list[QAReference] = []
    confidence: float = 0.8


class ArenaPersonality(str, Enum):
    WISHDEL = "wishdel"
    TERESIA = "teresia"


class ArenaRound(BaseModel):
    round: int
    question: str
    options: list[str] = []
    correct_answer: str = ""
    explanation: str = ""
    source: str = ""
    user_answer: str = ""
    opponent_answers: dict[str, str] = {}
    is_correct: Optional[bool] = None
    taunts: dict[str, str] = {}


class ArenaSession(BaseModel):
    id: str
    mode: str = "student"
    total_rounds: int = 8
    current_round: int = 0
    rounds: list[ArenaRound] = []
    user_score: int = 0
    streak: int = 0
    max_streak: int = 0
    status: str = "ready"
