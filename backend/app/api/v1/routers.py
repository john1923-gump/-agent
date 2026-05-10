from fastapi import APIRouter
from app.api.v1 import document, knowledge, rag, agent

router = APIRouter()
router.include_router(document.router, prefix="/documents", tags=["documents"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
router.include_router(rag.router, prefix="/rag", tags=["rag"])
router.include_router(agent.router, prefix="/agent", tags=["agent"])
