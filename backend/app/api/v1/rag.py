from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.schemas.rag import RAGAnswerResponse
from app.services.retrieval import RetrievalService
from app.services.embedding import EmbeddingService
from app.models.rag import DocumentChunk
from uuid import uuid4

router = APIRouter()

# 全局 RAG 服务实例
_rag_service: Optional[RetrievalService] = None


class RAGQuery(BaseModel):
    question: str
    top_k: int = 5
    use_llm: bool = False  # 是否使用 LLM 生成答案


class ChunkPayload(BaseModel):
    document_id: str
    section_id: str
    text: str
    page: Optional[int] = None
    source_label: Optional[str] = None


@router.post("/add-chunks")
def add_chunks_to_index(chunks: list[ChunkPayload]):
    """添加文档块到 RAG 索引"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RetrievalService()
    
    chunk_objects = [
        DocumentChunk(
            id=str(uuid4()),
            document_id=chunk.document_id,
            section_id=chunk.section_id,
            text=chunk.text,
            page=chunk.page,
            source_label=chunk.source_label,
        )
        for chunk in chunks
    ]
    
    _rag_service.add_chunks(chunk_objects)
    
    return {
        "success": True,
        "message": f"已添加 {len(chunk_objects)} 个文档块到索引",
        "chunk_count": len(chunk_objects),
    }


@router.post("/query", response_model=RAGAnswerResponse)
async def rag_query(payload: RAGQuery) -> RAGAnswerResponse:
    """RAG 查询接口，检索相关文档块并生成答案"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RetrievalService()
    
    # 执行检索
    results = _rag_service.query(payload.question, top_k=payload.top_k)
    
    if not results:
        return RAGAnswerResponse(
            success=False,
            question=payload.question,
            answer="未找到相关的教材内容，请尝试其他问题。",
            sources=[],
        )
    
    # 构建答案和引用来源
    sources = []
    source_texts = []
    
    for result in results:
        source_info = f"[{result.source_document}] {result.section_title}"
        if result.page:
            source_info += f" (第{result.page}页)"
        sources.append(source_info)
        source_texts.append(result.text)
    
    # 简单的答案生成：使用检索到的内容摘要
    answer = _generate_answer(payload.question, source_texts, payload.use_llm)
    
    return RAGAnswerResponse(
        success=True,
        question=payload.question,
        answer=answer,
        sources=sources,
    )


def _generate_answer(question: str, source_texts: list[str], use_llm: bool = False) -> str:
    """基于检索结果生成答案"""
    
    if use_llm:
        # TODO: 集成 OpenAI 或兼容 API 进行更智能的答案生成
        answer = f"基于教材内容，关于'{question}'的解答：\n"
        answer += "\n".join([f"- {text[:150]}..." for text in source_texts[:3]])
    else:
        # 简单的答案拼接
        answer = "根据教材查询结果：\n"
        answer += "\n".join([f"{i + 1}. {text[:200]}" for i, text in enumerate(source_texts[:3])])
    
    return answer


@router.get("/status")
def get_rag_status():
    """获取 RAG 索引状态"""
    global _rag_service
    
    if _rag_service is None or not _rag_service.chunks:
        return {"status": "empty", "chunk_count": 0}
    
    return {
        "status": "ready",
        "chunk_count": len(_rag_service.chunks),
        "index_built": _rag_service.index is not None,
    }


@router.delete("/clear")
def clear_rag_index():
    """清空 RAG 索引"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RetrievalService()
    else:
        _rag_service.clear()
    
    return {"success": True, "message": "已清空 RAG 索引"}
