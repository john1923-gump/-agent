from fastapi import APIRouter
from .textbooks import router as textbooks_router
from .knowledge import router as knowledge_router
from .qa import router as qa_router
from .arena import router as arena_router

api_router = APIRouter()
api_router.include_router(textbooks_router)
api_router.include_router(knowledge_router)
api_router.include_router(qa_router)
api_router.include_router(arena_router)


@api_router.get("/health")
async def health():
    return {"status": "ok", "app": "学科知识整合智能体"}
