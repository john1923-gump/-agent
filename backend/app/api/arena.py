from fastapi import APIRouter, HTTPException
from ..models.schemas import ArenaStartRequest, ArenaAnswerRequest
from ..services import arena_service

router = APIRouter(prefix="/api/arena", tags=["arena"])


@router.get("/opponents")
async def get_opponents():
    return [o.model_dump() for o in arena_service.get_opponents()]


@router.post("/start")
async def start_session(req: ArenaStartRequest):
    session = await arena_service.start_session(req)
    question = await arena_service.prepare_round(session, req.textbook_filter)
    return {
        "session": session.model_dump(),
        "question": question.model_dump(),
    }


@router.post("/answer")
async def submit_answer(req: ArenaAnswerRequest):
    session = arena_service.get_session(req.session_id)
    if not session:
        raise HTTPException(404, "会话未找到")
    if session.finished:
        raise HTTPException(400, "对局已结束")

    round_result = await arena_service.play_round(session, req.answer)

    next_question = None
    if not session.finished:
        next_question = await arena_service.prepare_round(session)

    return {
        "round": round_result.model_dump(),
        "session": session.model_dump(),
        "next_question": next_question.model_dump() if next_question else None,
    }


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    session = arena_service.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话未找到")
    return session.model_dump()
