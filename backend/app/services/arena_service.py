import logging
from ..models.schemas import (
    ArenaSession, ArenaRound, ArenaQuestion, ArenaOpponent,
    ArenaStartRequest, ArenaAnswerRequest
)
from ..utils.text_utils import gen_id
from . import llm_service, rag_service, graph_service

logger = logging.getLogger(__name__)

sessions_db: dict[str, ArenaSession] = {}

OPPONENTS = [
    ArenaOpponent(
        id="wishdel", name="维什戴尔",
        personality="自信张扬、争强好胜，总觉得自己是最聪明的",
        style="简洁犀利、喜欢用反问句和挑衅语气，偶尔引用战争典故"
    ),
    ArenaOpponent(
        id="teresia", name="特雷西娅",
        personality="沉稳冷静、理性分析型，表面温和实则暗藏锋芒",
        style="温和但暗含讽刺、喜欢引用典故和科学术语，用优雅的方式嘲笑对手"
    ),
]

STREAK_TAUNTS = {
    1: {
        "wishdel": "哟，失误了？我还以为你很厉害呢。",
        "teresia": "没关系，一次失误说明不了什么……大概吧。",
    },
    2: {
        "wishdel": "连续两题都不会？你确定你是来比赛的？",
        "teresia": "看来这道题确实有些难度呢，不过我倒是答对了。",
    },
    3: {
        "wishdel": "三连错！你是来搞笑的吗？我都替你着急！",
        "teresia": "哎呀，三题全错……我建议你回去重新翻翻教材呢。",
    },
}


async def start_session(req: ArenaStartRequest) -> ArenaSession:
    session = ArenaSession(
        id=gen_id(),
        mode=req.mode,
    )
    sessions_db[session.id] = session
    return session


async def generate_question(session: ArenaSession, textbook_filter: str | None = None) -> ArenaQuestion:
    difficulty = min(session.current_round // 3 + 1, 3)

    chunks = rag_service.get_all_chunks()
    if chunks:
        if textbook_filter:
            chunks = [c for c in chunks if c.textbook_id == textbook_filter]
        if chunks:
            try:
                q_data = await llm_service.generate_rag_arena_question(chunks, difficulty)
                return ArenaQuestion(
                    id=gen_id(),
                    question=q_data.get("question", ""),
                    options=q_data.get("options", []),
                    correct_answer=q_data.get("correct_answer", "A"),
                    explanation=q_data.get("explanation", ""),
                    knowledge_point_id="",
                    knowledge_point_name=q_data.get("source", "综合"),
                    difficulty=difficulty,
                )
            except Exception as e:
                logger.warning(f"RAG出题失败，回退到知识点出题: {e}")

    kps = graph_service.get_all_knowledge_points()
    if not kps:
        return ArenaQuestion(
            id=gen_id(),
            question="请简述学习的重要性。",
            options=["A.获取知识和技能", "B.浪费时间", "C.毫无意义", "D.以上都不对"],
            correct_answer="A",
            explanation="学习是获取知识和技能的基本途径",
            knowledge_point_id="",
            knowledge_point_name="通用",
            difficulty=1,
        )

    import random
    kp = random.choice(kps)
    q_data = await llm_service.generate_arena_question(kp.name, kp.description, difficulty)

    return ArenaQuestion(
        id=gen_id(),
        question=q_data.get("question", ""),
        options=q_data.get("options", []),
        correct_answer=q_data.get("correct_answer", "A"),
        explanation=q_data.get("explanation", ""),
        knowledge_point_id=kp.id,
        knowledge_point_name=kp.name,
        difficulty=difficulty,
    )


async def play_round(session: ArenaSession, answer: str) -> ArenaRound:
    if not session.rounds or session.last_question is None:
        question = await generate_question(session)
    else:
        question = session.last_question

    difficulty = question.difficulty

    opponent_answers = {}
    for opp in OPPONENTS:
        try:
            opp_ans = await llm_service.generate_arena_opponent_answer(
                opp.name, opp.personality, question.question, question.options, question.correct_answer
            )
        except Exception:
            import random
            opp_ans = question.correct_answer if random.random() < 0.55 else random.choice(
                [o for o in question.options if not o.startswith(question.correct_answer[0])]
            ) if question.options else question.correct_answer
        opponent_answers[opp.name] = opp_ans

    judgment = await llm_service.judge_arena_answer(
        question.question, question.correct_answer, answer, question.explanation
    )
    is_correct = judgment.get("is_correct", False)
    feedback = judgment.get("feedback", "")

    if is_correct:
        session.score += 10 * difficulty
        session.streak += 1
        session.max_streak = max(session.max_streak, session.streak)
    else:
        session.streak = 0
        session.weak_points.append(question.knowledge_point_name)

    wrong_streak = 0
    for r in reversed(session.rounds):
        if not r.is_correct:
            wrong_streak += 1
        else:
            break

    opponent_comments = {}
    for opp in OPPONENTS:
        try:
            comment = await llm_service.opponent_comment(
                opp.name, opp.personality, opp.style,
                is_correct, answer, wrong_streak if not is_correct else 0
            )
        except Exception:
            if is_correct:
                comment = f"哼，算你厉害！——{opp.name}"
            else:
                taunt_key = min(wrong_streak, 3)
                comment = STREAK_TAUNTS.get(taunt_key, {}).get(opp.id, f"这都不会？——{opp.name}")
        opponent_comments[opp.name] = comment

    arena_round = ArenaRound(
        round_num=session.current_round + 1,
        question=question,
        opponent_answers=opponent_answers,
        user_answer=answer,
        is_correct=is_correct,
        feedback=feedback,
        opponent_comments=opponent_comments,
    )
    session.rounds.append(arena_round)
    session.current_round += 1
    if session.current_round >= 8:
        session.finished = True

    session.last_question = None
    return arena_round


async def prepare_round(session: ArenaSession, textbook_filter: str | None = None) -> ArenaQuestion:
    question = await generate_question(session, textbook_filter)
    session.last_question = question
    return question


def get_session(session_id: str) -> ArenaSession | None:
    return sessions_db.get(session_id)


def get_opponents() -> list[ArenaOpponent]:
    return OPPONENTS
