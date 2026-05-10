from fastapi import APIRouter
from app.schemas.knowledge import KnowledgeGraphResponse

router = APIRouter()

@router.get("/graph", response_model=KnowledgeGraphResponse)
def get_knowledge_graph() -> KnowledgeGraphResponse:
    return KnowledgeGraphResponse(
        success=True,
        message="知识图谱查询接口已就绪",
        graph={"nodes": [], "edges": []},
    )
