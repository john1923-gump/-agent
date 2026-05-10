from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TextbookMeta(BaseModel):
    id: str
    filename: str
    format: str
    chapter_count: int = 0
    upload_time: str = ""


class Chapter(BaseModel):
    id: str
    textbook_id: str
    textbook_name: str
    title: str
    content: str
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
    page: int = 0
    embedding: Optional[list[float]] = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: KnowledgeType
    textbook_id: str
    textbook_name: str
    chapter_title: str = ""
    description: str = ""
    frequency: int = 1
    size: int = 20


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str = "相关"
    weight: float = 1.0


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class Chunk(BaseModel):
    id: str
    textbook_id: str
    textbook_name: str
    chapter_id: str
    chapter_title: str
    content: str
    page: int = 0
    embedding: Optional[list[float]] = None


class IntegrationDecision(str, Enum):
    MERGE = "merge"
    KEEP = "keep"
    REMOVE = "remove"


class IntegrationPair(BaseModel):
    kp_a: KnowledgePoint
    kp_b: KnowledgePoint
    similarity: float
    decision: IntegrationDecision
    reason: str
    merged_content: Optional[str] = None


class IntegrationResult(BaseModel):
    pairs: list[IntegrationPair] = []
    compression_ratio: float = 0.0
    original_count: int = 0
    final_count: int = 0
    original_text_chars: int = 0
    final_text_chars: int = 0
    merge_count: int = 0
    keep_count: int = 0
    remove_count: int = 0
    integrity_report: dict = Field(default_factory=dict)
    coverage_report: dict = Field(default_factory=dict)


class QARequest(BaseModel):
    question: str
    textbook_filter: Optional[str] = None


class QAReference(BaseModel):
    textbook_name: str
    chapter_title: str
    page: int
    snippet: str


class QAResponse(BaseModel):
    answer: str
    references: list[QAReference] = []


class ChatMessage(BaseModel):
    role: str
    content: str


class TeacherChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class TeacherChatResponse(BaseModel):
    reply: str
    graph_updated: bool = False


class ArenaOpponent(BaseModel):
    id: str
    name: str
    personality: str
    style: str


class ArenaQuestion(BaseModel):
    id: str
    question: str
    options: list[str] = []
    correct_answer: str
    explanation: str
    knowledge_point_id: str
    knowledge_point_name: str
    difficulty: int = 1


class ArenaRound(BaseModel):
    round_num: int
    question: ArenaQuestion
    opponent_answers: dict[str, str] = {}
    user_answer: str = ""
    is_correct: bool = False
    feedback: str = ""
    opponent_comments: dict[str, str] = {}


class ArenaSession(BaseModel):
    id: str
    mode: str = "student"
    rounds: list[ArenaRound] = []
    current_round: int = 0
    score: int = 0
    streak: int = 0
    max_streak: int = 0
    weak_points: list[str] = []
    finished: bool = False
    _last_question: Optional[ArenaQuestion] = None

    class Config:
        arbitrary_types_allowed = True


class ArenaStartRequest(BaseModel):
    mode: str = "student"
    textbook_filter: Optional[str] = None


class ArenaAnswerRequest(BaseModel):
    session_id: str
    answer: str
