from typing import Dict
from app.models.agent import AgentPersona, DialogueTurn, EvaluationResult


class AgentService:
    def __init__(self):
        self.personas: Dict[str, AgentPersona] = {}

    def register_persona(self, persona: AgentPersona):
        self.personas[persona.id] = persona

    def plan(self, prompt: str, persona_id: str | None = None) -> str:
        persona = self.personas.get(persona_id)
        return f"已接收计划请求：{prompt}，persona={persona.name if persona else 'default'}"

    def evaluate_response(self, answer: str, reference: str) -> EvaluationResult:
        return EvaluationResult(score=0.0, feedback="评估模块待实现", weak_points=[])
