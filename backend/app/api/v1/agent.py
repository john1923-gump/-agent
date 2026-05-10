from fastapi import APIRouter
from app.schemas.agent import AgentResponse

router = APIRouter()

@router.post("/plan", response_model=AgentResponse)
def agent_plan() -> AgentResponse:
    return AgentResponse(success=True, message="Agent架构说明接口已就绪")
