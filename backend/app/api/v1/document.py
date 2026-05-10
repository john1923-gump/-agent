from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.document import DocumentUploadResponse
from app.services.parser import parse_uploaded_document

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    if file.content_type not in ["application/pdf", "text/markdown", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=415, detail="不支持的文件类型")

    document = await parse_uploaded_document(file)
    return DocumentUploadResponse(success=True, document=document)
