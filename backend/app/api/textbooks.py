"""教材管理API：上传、解析、知识提取、RAG分块、图谱构建。"""
import os
import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from ..config import settings
from ..models.schemas import TextbookMeta, TextbookFormat
from ..services import parser_service, rag_service, graph_service
from ..utils.text_utils import gen_id, calc_checksum

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/textbooks", tags=["textbooks"])

textbooks_db: dict[str, TextbookMeta] = {}


async def _extract_knowledge_background(chapters, filename):
    """后台知识提取任务。"""
    try:
        kps = await graph_service.extract_and_build(chapters)
        kp_count = len(kps)
        logger.info(f"知识提取完成: {filename} -> {kp_count} 个知识点")
    except Exception as e:
        logger.warning(f"知识提取失败（不影响上传）: {e}")


@router.post("/upload")
async def upload_textbook(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "请选择文件")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的格式: {ext}。支持: {', '.join(settings.ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "文件过大")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{gen_id()}{ext}")

    with open(file_path, "wb") as f:
        f.write(content)

    textbook_id = gen_id()
    checksum = calc_checksum(content)
    fmt, error = parser_service.detect_format(file_path, file.filename)
    if error:
        os.remove(file_path)
        raise HTTPException(400, error)

    meta = TextbookMeta(
        id=textbook_id, filename=file.filename, format=fmt,
        checksum=checksum, upload_time=datetime.now().isoformat(),
    )

    chapters, error = parser_service.parse(file_path, meta)
    if error:
        os.remove(file_path)
        raise HTTPException(500, error)

    meta.chapter_count = len(chapters)
    textbooks_db[textbook_id] = meta

    rag_service.add_textbook_chunks(textbook_id, file.filename, chapters)

    asyncio.create_task(_extract_knowledge_background(chapters, file.filename))

    graph = graph_service.get_graph()

    return {
        "textbook": meta.model_dump(),
        "chapter_count": len(chapters),
        "knowledge_points": 0,
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
    }


@router.get("/list")
async def list_textbooks():
    return list(textbooks_db.values())
