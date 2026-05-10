from fastapi import APIRouter, HTTPException
from ..models.schemas import IntegrationResult
from ..services import graph_service, integration_service, rag_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/graph")
async def get_knowledge_graph():
    return graph_service.get_graph().model_dump()


@router.get("/points")
async def get_all_knowledge_points():
    return [kp.model_dump() for kp in graph_service.get_all_knowledge_points()]


@router.get("/points/{kp_id}")
async def get_knowledge_point(kp_id: str):
    kp = graph_service.get_knowledge_point(kp_id)
    if not kp:
        raise HTTPException(404, "知识点未找到")
    return kp.model_dump()


@router.post("/integrate")
async def integrate_knowledge():
    kps = graph_service.get_all_knowledge_points()
    if len(kps) < 2:
        return {"message": "知识点不足，需要至少2个知识点", "result": None}

    all_chunks = rag_service.get_all_chunks()
    original_text_chars = sum(len(c.content) for c in all_chunks) if all_chunks else 0

    result = await integration_service.integrate_cross_textbooks(kps, original_text_chars)
    return {"result": result.model_dump()}


@router.post("/integrate/apply")
async def apply_integration(result: IntegrationResult):
    integration_service.apply_integration(result)
    return {"status": "ok", "graph": graph_service.get_graph().model_dump()}


@router.get("/rag/stats")
async def get_rag_stats():
    return {
        "chunk_count": rag_service.get_chunk_count(),
        "chunks": [
            {
                "id": c.id,
                "textbook_name": c.textbook_name,
                "chapter_title": c.chapter_title,
                "content_length": len(c.content),
            }
            for c in rag_service.get_all_chunks()[:20]
        ],
    }
