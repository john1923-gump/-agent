from typing import List
from pydantic import BaseModel


class RAGAnswerResponse(BaseModel):
    success: bool
    question: str
    answer: str
    sources: List[str]
