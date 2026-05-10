"""LLM服务：调用大语言模型API。"""
import json
import logging
import asyncio
from openai import AsyncOpenAI
from ..config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    max_retries=2,
    timeout=60.0,
)


async def chat(messages: list[dict], model: str | None = None, temperature: float = 0.3) -> str:
    """调用LLM聊天接口。"""
    resp = await client.chat.completions.create(
        model=model or settings.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


async def chat_stream(messages: list[dict], model: str | None = None, temperature: float = 0.3):
    """调用LLM流式聊天接口。"""
    stream = await client.chat.completions.create(
        model=model or settings.LLM_MODEL,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


EXTRACTION_EXAMPLES = """示例1（概念类型）：
{"name": "细胞膜", "description": "细胞的外层膜结构，由磷脂双分子层和蛋白质组成，具有流动性和选择透过性", "type": "概念", "confidence": 0.95}

示例2（定理类型）：
{"name": "牛顿第二定律", "description": "物体加速度的大小与作用力成正比，与物体质量成反比，F=ma", "type": "定理", "confidence": 0.98}

示例3（方法类型）：
{"name": "差速离心法", "description": "利用不同离心速度分离细胞器的方法，依次在不同转速下离心分离大小不同的颗粒", "type": "方法", "confidence": 0.88}

示例4（现象类型）：
{"name": "渗透作用", "description": "水分子通过半透膜从低浓度溶液向高浓度溶液扩散的现象", "type": "现象", "confidence": 0.92}"""


async def extract_knowledge_points(chapter_content: str, chapter_title: str) -> dict:
    """从章节内容中提取知识点和关系。"""
    prompt = f"""你是学科知识提取专家。请从以下教材章节中提取所有知识点及其关系。

章节标题：{chapter_title}

章节内容：
{chapter_content[:3000]}

请以JSON格式返回，包含两个字段：
1. knowledge_points: 知识点数组，每个包含：
   - name: 知识点名称
   - description: 知识点描述（1-2句话，50-150字）
   - type: 类型（必须是"概念"、"定理"、"方法"或"现象"之一）
   - confidence: 置信度分数（0-1之间，表示对该知识点提取的把握程度）
2. relationships: 关系数组，每个包含：
   - source: 源知识点名称
   - target: 目标知识点名称
   - relation: 关系类型（必须是"prerequisite"、"parallel"、"contains"、"applies_to"之一）
   - description: 关系简述

知识点提取示例：
{EXTRACTION_EXAMPLES}

只返回JSON，不要其他文字。"""

    try:
        result = await chat([{"role": "user", "content": prompt}], temperature=0.1)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        parsed = json.loads(result)

        for kp in parsed.get("knowledge_points", []):
            if "confidence" not in kp:
                kp["confidence"] = 0.8
            kp["confidence"] = max(0.0, min(1.0, float(kp.get("confidence", 0.8))))

        return parsed
    except Exception as e:
        logger.warning(f"知识提取失败: {e}")
        return {"knowledge_points": [], "relationships": []}


async def judge_arena_answer(question: str, correct_answer: str, user_answer: str, explanation: str) -> dict:
    """判断竞技场答题是否正确。"""
    prompt = f"""判断以下学生回答是否正确。

题目：{question}
标准答案：{correct_answer}
学生回答：{user_answer}
解析：{explanation}

请返回JSON格式：
{{"is_correct": true/false, "feedback": "简要评价（50字以内）"}}"""

    try:
        result = await chat([{"role": "user", "content": prompt}], temperature=0.1)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except Exception:
        keywords = correct_answer.lower().split()
        matched = sum(1 for k in keywords if k in user_answer.lower())
        is_correct = matched >= len(keywords) * 0.5
        return {
            "is_correct": is_correct,
            "feedback": "回答基本正确。" if is_correct else f"正确答案是：{correct_answer}"
        }


async def generate_arena_question(knowledge_name: str, knowledge_desc: str, difficulty: int = 1) -> dict:
    """生成竞技场选择题。"""
    diff_map = {1: "基础", 2: "中等", 3: "困难"}
    prompt = f"""基于以下知识点生成一道{diff_map.get(difficulty, '基础')}难度的选择题。

知识点：{knowledge_name}
描述：{knowledge_desc}

请返回JSON格式：
{{"question": "题目内容", "options": ["A.选项1", "B.选项2", "C.选项3", "D.选项4"], "correct_answer": "A", "explanation": "解析"}}"""

    try:
        result = await chat([{"role": "user", "content": prompt}], temperature=0.7)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except Exception as e:
        logger.warning(f"生成题目失败: {e}")
        return {
            "question": f"关于{knowledge_name}，以下说法正确的是？",
            "options": ["A.正确", "B.错误", "C.不确定", "D.以上都不对"],
            "correct_answer": "A",
            "explanation": knowledge_desc
        }


async def opponent_comment(opponent_name: str, personality: str, style: str,
                           is_user_correct: bool, user_answer: str, streak_wrong: int) -> str:
    """生成对手评论。"""
    taunt_level = min(streak_wrong, 3)
    if is_user_correct:
        prompt = f"你是{opponent_name}，性格{personality}，说话风格{style}。对手答对了题目。请用一句话表达不甘心但认可的语气。"
    else:
        prompt = f"你是{opponent_name}，性格{personality}，说话风格{style}。对手答错了，已连续答错{streak_wrong}题。嘲讽等级{taunt_level}/3。请用一句话嘲讽对手，等级越高越毒舌。"

    try:
        return await chat([{"role": "user", "content": prompt}], temperature=0.8)
    except Exception:
        if is_user_correct:
            return f"哼，算你厉害！——{opponent_name}"
        return f"这都不会？哈哈！——{opponent_name}"


async def generate_arena_opponent_answer(opponent_name: str, personality: str,
                                          question: str, options: list[str], correct: str) -> str:
    """生成对手答题。"""
    prompt = f"""你是{opponent_name}，性格{personality}。请回答以下选择题，只需返回选项字母（A/B/C/D之一）。

题目：{question}
选项：
{chr(10).join(options)}

直接返回一个字母，不要其他文字。"""

    try:
        result = await chat([{"role": "user", "content": prompt}], temperature=0.6)
        letter = result.strip().upper()
        if letter and letter[0] in 'ABCD':
            for opt in options:
                if opt.startswith(letter[0]):
                    return opt
    except Exception:
        pass
    import random
    if random.random() < 0.55:
        return correct
    wrong = [o for o in options if not o.startswith(correct[0])]
    return random.choice(wrong) if wrong else correct


async def teacher_chat_reply(message: str, history: list[dict],
                             graph_context: str, integration_context: str) -> str:
    """生成教师对话回复。"""
    system = f"""你是一位资深学科教师助手，专门帮助教师审查和调整跨教材知识整合方案。

当前知识图谱概况：
{graph_context}

{integration_context}

你的能力：
1. 解释整合决策的原因（为什么合并/保留/移除某个知识点）
2. 根据教师反馈修改决策（如"把XX和YY改为保留而不是合并"）
3. 回答关于知识图谱结构的问题
4. 建议进一步的整合优化方向

回答要求：
- 引用具体知识点名称和教材来源
- 如果教师要求修改决策，在回答中明确说明修改内容，以[UPDATE_DECISION]标记
- 语言亲切专业，适合教师阅读"""

    messages = [{"role": "system", "content": system}]
    for h in history[-10:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    return await chat(messages, temperature=0.4)


async def generate_rag_arena_question(chunks: list, difficulty: int = 1) -> dict:
    """基于RAG文档块生成竞技场题目。"""
    import random
    selected = random.sample(chunks, min(3, len(chunks)))
    context = "\n\n".join([f"【{c.chapter_title}】\n{c.content[:300]}" for c in selected])
    diff_map = {1: "基础", 2: "中等", 3: "困难"}

    prompt = f"""基于以下教材内容，生成一道{diff_map.get(difficulty, '基础')}难度的选择题。

教材内容：
{context}

要求：
- 题目必须基于上述教材内容
- 4个选项，只有一个正确
- 提供解析

返回JSON格式：
{{"question": "题目内容", "options": ["A.选项1", "B.选项2", "C.选项3", "D.选项4"], "correct_answer": "A", "explanation": "解析", "source": "来源章节"}}"""

    try:
        result = await chat([{"role": "user", "content": prompt}], temperature=0.7)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        data = json.loads(result)
        data.setdefault("source", selected[0].chapter_title if selected else "")
        return data
    except Exception as e:
        logger.warning(f"RAG出题失败: {e}")
        return {
            "question": f"关于{selected[0].chapter_title if selected else '学习'}，以下说法正确的是？",
            "options": ["A.正确", "B.错误", "C.不确定", "D.以上都不对"],
            "correct_answer": "A",
            "explanation": selected[0].content[:100] if selected else "",
            "source": selected[0].chapter_title if selected else "",
        }
