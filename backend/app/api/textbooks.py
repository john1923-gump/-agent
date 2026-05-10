import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..config import settings
from ..services import parser_service, rag_service, graph_service

router = APIRouter(prefix="/api/textbooks", tags=["textbooks"])

textbooks_db: dict[str, dict] = {}


@router.post("/upload")
async def upload_textbook(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "文件名为空")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.pdf', '.docx', '.md', '.txt'):
        raise HTTPException(400, f"不支持的格式: {ext}")

    save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        meta, chapters = parser_service.parse_textbook(save_path, file.filename)
    except Exception as e:
        raise HTTPException(500, f"解析失败: {str(e)}")

    textbooks_db[meta.id] = {"meta": meta.model_dump(), "chapters": [c.model_dump() for c in chapters]}

    rag_service.add_textbook_chunks(meta.id, meta.filename, chapters)

    kps = await graph_service.extract_and_build(chapters)

    return {
        "textbook": meta.model_dump(),
        "chapters_count": len(chapters),
        "knowledge_points_count": len(kps),
        "chunks_count": rag_service.get_chunk_count(),
    }


@router.get("/list")
async def list_textbooks():
    return list(textbooks_db.values())


@router.get("/{textbook_id}")
async def get_textbook(textbook_id: str):
    tb = textbooks_db.get(textbook_id)
    if not tb:
        raise HTTPException(404, "教材未找到")
    return tb


@router.delete("/{textbook_id}")
async def delete_textbook(textbook_id: str):
    if textbook_id in textbooks_db:
        del textbooks_db[textbook_id]
        return {"status": "ok"}
    raise HTTPException(404, "教材未找到")
