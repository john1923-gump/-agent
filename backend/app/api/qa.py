import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..models.schemas import QARequest, QAResponse, QAReference, TeacherChatRequest, TeacherChatResponse
from ..services import rag_service, llm_service, graph_service

router = APIRouter(prefix="/api/qa", tags=["qa"])


@router.post("/ask")
async def ask_question(req: QARequest):
    try:
        results = rag_service.retrieve(req.question, top_k=5, textbook_filter=req.textbook_filter)

        context_parts = []
        references = []
        for chunk, score in results:
            context_parts.append(f"[来源:《{chunk.textbook_name}》{chunk.chapter_title}, 第{chunk.page}页, 相关度{score:.2f}]\n{chunk.content}")
            references.append(QAReference(
                textbook_name=chunk.textbook_name,
                chapter_title=chunk.chapter_title,
                page=chunk.page,
                snippet=chunk.content[:200],
            ))

        if context_parts:
            context = "\n\n---\n\n".join(context_parts)
            system_prompt = "你是一个学科知识助手。严格根据提供的教材内容回答问题，必须在回答中引用来源（如[来源:《教材名》章节]）。如果参考资料不足以完整回答问题，请明确说明哪些部分有据可查、哪些是推测。"
            user_prompt = f"参考资料：\n{context}\n\n问题：{req.question}\n\n请用中文回答，回答中必须标注引用来源。"
        else:
            system_prompt = "你是一个学科知识助手。当前知识库中没有找到与问题相关的教材内容，请如实告知用户，并建议他们先上传相关教材。"
            user_prompt = f"问题：{req.question}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        answer = await llm_service.chat(messages)
        return QAResponse(answer=answer, references=references).model_dump()
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            return QAResponse(
                answer="⚠️ API调用额度已用完，请明天再试或更换API密钥。以下是从知识库检索到的相关内容：\n\n" + "\n\n".join(
                    f"📖 {r.textbook_name} - {r.chapter_title}\n{r.snippet}" for r in references
                ) if references else "⚠️ API额度已用完，请明天再试。",
                references=references if references else [],
            ).model_dump()
        raise


@router.post("/ask/stream")
async def ask_question_stream(req: QARequest):
    results = rag_service.retrieve(req.question, top_k=5, textbook_filter=req.textbook_filter)

    context_parts = []
    refs = []
    for chunk, score in results:
        context_parts.append(f"[来源:《{chunk.textbook_name}》{chunk.chapter_title}, 第{chunk.page}页, 相关度{score:.2f}]\n{chunk.content}")
        refs.append({
            "textbook_name": chunk.textbook_name,
            "chapter_title": chunk.chapter_title,
            "page": chunk.page,
            "snippet": chunk.content[:200],
            "score": round(score, 3),
        })

    async def event_generator():
        yield f"data: {json.dumps({'type': 'references', 'data': refs})}\n\n"

        if context_parts:
            context = "\n\n---\n\n".join(context_parts)
            system_prompt = "你是一个学科知识助手。严格根据提供的教材内容回答问题，必须在回答中引用来源（如[来源:《教材名》章节]）。如果参考资料不足以完整回答问题，请明确说明哪些部分有据可查、哪些是推测。"
            user_prompt = f"参考资料：\n{context}\n\n问题：{req.question}\n\n请用中文回答，回答中必须标注引用来源。"
        else:
            system_prompt = "你是一个学科知识助手。当前知识库中没有找到与问题相关的教材内容，请如实告知用户，并建议他们先上传相关教材。"
            user_prompt = f"问题：{req.question}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        async for token in llm_service.chat_stream(messages):
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/teacher-chat")
async def teacher_chat(req: TeacherChatRequest):
    kps = graph_service.get_all_knowledge_points()
    graph_context = f"共{len(kps)}个知识点：\n"
    graph_context += "\n".join([f"- {kp.name}({kp.type.value}): {kp.description[:60]} [《{kp.textbook_name}》{kp.chapter_title}]" for kp in kps[:30]])

    graph = graph_service.get_graph()
    integration_context = f"知识图谱：{len(graph.nodes)}个节点，{len(graph.edges)}条边\n"
    integration_context += "关系类型分布："
    rel_counts: dict[str, int] = {}
    for e in graph.edges:
        rel_counts[e.relation] = rel_counts.get(e.relation, 0) + 1
    integration_context += "、".join([f"{k}({v})" for k, v in rel_counts.items()])

    history_dicts = [{"role": msg.role, "content": msg.content} for msg in req.history]

    try:
        reply = await llm_service.teacher_chat_reply(
            req.message, history_dicts, graph_context, integration_context
        )
    except Exception:
        messages = [
            {"role": "system", "content": f"你是教学助手。\n{graph_context}\n\n{integration_context}"},
        ]
        for msg in req.history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": req.message})
        reply = await llm_service.chat(messages)

    graph_updated = False

    import re
    actions = re.findall(r'\[ACTION:(\w+)(?::([^\]]+))?\]', reply)
    for action_type, params in actions:
        if action_type == "UPDATE_KP" and params:
            parts = params.split(":", 1)
            if len(parts) == 2:
                kp_id, field_val = parts
                if "=" in field_val:
                    field, val = field_val.split("=", 1)
                    graph_service.update_knowledge_point(kp_id.strip(), {field.strip(): val.strip()})
                    graph_updated = True
        elif action_type == "REMOVE_KP" and params:
            graph_service.remove_knowledge_point(params.strip())
            graph_updated = True

    return TeacherChatResponse(reply=reply, graph_updated=graph_updated).model_dump()
