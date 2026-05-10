"""数据模型定义：Pydantic schemas。"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TextbookFormat(str, Enum):
    """教材格式枚举。"""
    PDF = "pdf"
    DOCX = "docx"
    MD = "md"
    TXT = "txt"


class TextbookMeta(BaseModel):
    """教材元数据。"""
    id: str
    filename: str
    format: TextbookFormat
    chapter_count: int = 0
    checksum: str = ""
    upload_time: str = ""


class Chapter(BaseModel):
    """章节数据。"""
    id: str = ""
    textbook_id: str = ""
    textbook_name: str = ""
    title: str = ""
    content: str = ""
    page_start: int = 0
    page_end: int = 0


class KnowledgeType(str, Enum):
    """知识点类型枚举。"""
    CONCEPT = "概念"
    THEOREM = "定理"
    METHOD = "方法"
    PHENOMENON = "现象"


class KnowledgePoint(BaseModel):
    """知识点。"""
    id: str
    chapter_id: str = ""
    textbook_id: str = ""
    textbook_name: str = ""
    chapter_title: str = ""
    name: str
    description: str
    type: KnowledgeType
    confidence: float = 0.8
    relations: list[str] = []


class RelationType(str, Enum):
    """关系类型枚举。"""
    PREREQUISITE = "prerequisite"
    PARALLEL = "parallel"
    CONTAINS = "contains"
    APPLIES_TO = "applies_to"


class GraphNode(BaseModel):
    """图谱节点。"""
    id: str
    label: str
    type: str
    textbook_id: str = ""
    textbook_name: str = ""
    frequency: int = 1
    size: int = 20
    chapter_title: str = ""
    description: str = ""
    confidence: float = 0.8


class GraphEdge(BaseModel):
    """图谱边。"""
    source: str
    target: str
    relation: str = "关联"
    weight: float = 1.0


class KnowledgeGraph(BaseModel):
    """知识图谱（包含节点和边）。"""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class IntegrationDecision(str, Enum):
    """整合决策枚举。"""
    MERGE = "merge"
    KEEP = "keep"
    REMOVE = "remove"
    ENRICH = "enrich"


class IntegrationPair(BaseModel):
    """整合配对。"""
    kp_a: KnowledgePoint
    kp_b: KnowledgePoint
    similarity: float
    decision: IntegrationDecision
    reason: str
    merged_content: Optional[str] = None


class IntegrationResult(BaseModel):
    """整合结果。"""
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
    """文档块（用于RAG检索）。"""
    id: str
    textbook_id: str
    textbook_name: str
    chapter_id: str
    chapter_title: str
    content: str
    page: int = 0


class QAReference(BaseModel):
    """问答引用来源。"""
    textbook_name: str = ""
    chapter_title: str = ""
    page: int = 0
    snippet: str = ""


class QAResponse(BaseModel):
    """问答响应。"""
    answer: str
    references: list[QAReference] = []
    confidence: float = 0.8


class ChatMessage(BaseModel):
    """对话消息。"""
    role: str
    content: str


class QARequest(BaseModel):
    """问答请求。"""
    question: str
    textbook_filter: Optional[str] = None


class TeacherChatRequest(BaseModel):
    """教师对话请求。"""
    message: str
    history: list[ChatMessage] = []


class TeacherChatResponse(BaseModel):
    """教师对话响应。"""
    reply: str
    graph_updated: bool = False


class ArenaPersonality(str, Enum):
    """竞技场对手性格。"""
    WISHDEL = "wishdel"
    TERESIA = "teresia"


class ArenaQuestion(BaseModel):
    """竞技场题目。"""
    id: str = ""
    question: str
    options: list[str] = []
    correct_answer: str = ""
    explanation: str = ""
    knowledge_point_id: str = ""
    knowledge_point_name: str = ""
    difficulty: int = 1


class ArenaRound(BaseModel):
    """竞技场回合。"""
    round_num: int = 0
    question: Optional[ArenaQuestion] = None
    user_answer: str = ""
    opponent_answers: dict[str, str] = {}
    is_correct: Optional[bool] = None
    feedback: str = ""
    opponent_comments: dict[str, str] = {}


class ArenaSession(BaseModel):
    """竞技场会话。"""
    id: str
    mode: str = "student"
    total_rounds: int = 8
    current_round: int = 0
    rounds: list[ArenaRound] = []
    score: int = 0
    streak: int = 0
    max_streak: int = 0
    weak_points: list[str] = []
    finished: bool = False
    last_question: Optional[ArenaQuestion] = None


class ArenaOpponent(BaseModel):
    """竞技场对手。"""
    id: str = ""
    name: str
    personality: str = ""
    style: str = ""
    avatar_url: str = ""
    description: str = ""


class ArenaStartRequest(BaseModel):
    """竞技场开始请求。"""
    mode: str = "student"
    textbook_filter: Optional[str] = None


class ArenaAnswerRequest(BaseModel):
    """竞技场答题请求。"""
    session_id: str
    answer: str
