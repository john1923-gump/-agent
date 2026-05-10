from typing import List
from pydantic import BaseModel
from app.models.document import DocumentStructure


class DocumentUploadResponse(BaseModel):
    success: bool
    document: DocumentStructure
