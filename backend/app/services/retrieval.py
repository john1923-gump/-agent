from typing import List, Optional
from uuid import uuid4
import numpy as np
from app.models.rag import DocumentChunk, RAGResult
from app.services.embedding import EmbeddingService


class RetrievalService:
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.chunks: List[DocumentChunk] = []
        self.index = None
        self.embeddings_matrix = None

    def add_chunks(self, chunks: List[DocumentChunk]):
        """添加文档块，并为其生成嵌入与索引"""
        self.chunks.extend(chunks)
        self._build_faiss_index()

    def _build_faiss_index(self):
        """基于所有块的文本构建 FAISS 索引"""
        if not self.chunks:
            return
        
        try:
            import faiss
        except ImportError:
            raise ImportError("请安装 FAISS: pip install faiss-cpu 或 faiss-gpu")
        
        texts = [chunk.text for chunk in self.chunks]
        embeddings = self.embedding_service.encode(texts, normalize=True)
        self.embeddings_matrix = np.array(embeddings, dtype=np.float32)
        
        if self.embeddings_matrix.size == 0:
            self.index = None
            return
        
        dimension = self.embeddings_matrix.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.embeddings_matrix)

    def query(self, query_text: str, top_k: int = 5) -> List[RAGResult]:
        """基于查询文本检索相关文档块"""
        if not self.chunks or self.index is None:
            return []
        
        query_embedding = self.embedding_service.encode_single(query_text, normalize=True)
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        distances, indices = self.index.search(query_vector, min(top_k, len(self.chunks)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            score = float(distances[0][i])
            
            result = RAGResult(
                text=chunk.text[:400],
                score=score,
                source_document=chunk.document_id,
                section_title=chunk.section_id,
                page=chunk.page,
                citations=[chunk.document_id],
            )
            results.append(result)
        
        return results

    def clear(self):
        """清空索引和块"""
        self.chunks = []
        self.index = None
        self.embeddings_matrix = None
