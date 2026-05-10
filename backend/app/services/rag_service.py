"""RAG检索服务：混合检索（TF-IDF + Embedding）与问答生成。"""
import os
import math
import logging
import numpy as np
from ..models.schemas import Chunk, QAReference
from ..config import settings
from ..utils.text_utils import gen_id, split_chunks
from . import embedding_service

logger = logging.getLogger(__name__)

_chunks_db: dict[str, Chunk] = {}
_chunk_id_list: list[str] = []
_tfidf_matrix: np.ndarray | None = None
_embedding_matrix: np.ndarray | None = None
_vocab: dict[str, int] = {}
_idf: np.ndarray | None = None

USE_HYBRID_RETRIEVAL = True
BM25_WEIGHT = 0.5
EMBED_WEIGHT = 0.5


def _char_ngrams(text: str, n: int = 2) -> list[str]:
    """生成文本的字符n-gram列表。

    Args:
        text: 输入文本。
        n: n-gram的n值。

    Returns:
        n-gram列表。
    """
    text = text.replace('\n', ' ').replace('\r', ' ')
    return [text[i:i+n] for i in range(len(text) - n + 1)]


def _build_vocab(texts: list[str]) -> dict[str, int]:
    """从文本列表构建词汇表。

    Args:
        texts: 文本列表。

    Returns:
        词汇到索引的映射字典。
    """
    vocab: dict[str, int] = {}
    for text in texts:
        for gram in _char_ngrams(text, 2):
            if gram not in vocab:
                vocab[gram] = len(vocab)
        for gram in _char_ngrams(text, 3):
            if gram not in vocab:
                vocab[gram] = len(vocab)
    return vocab


def _text_to_tfidf(text: str, vocab: dict[str, int], idf: np.ndarray) -> np.ndarray:
    """将文本转换为TF-IDF向量。

    Args:
        text: 输入文本。
        vocab: 词汇表。
        idf: IDF向量。

    Returns:
        TF-IDF向量。
    """
    tf = np.zeros(len(vocab), dtype=np.float32)
    grams = _char_ngrams(text, 2) + _char_ngrams(text, 3)
    for g in grams:
        if g in vocab:
            tf[vocab[g]] += 1
    total = len(grams) if grams else 1
    tf = tf / total
    return tf * idf


def _build_tfidf_index() -> None:
    """构建TF-IDF索引矩阵。"""
    global _tfidf_matrix, _vocab, _idf

    if not _chunk_id_list:
        _tfidf_matrix = None
        return

    texts = [_chunks_db[cid].content for cid in _chunk_id_list]
    _vocab = _build_vocab(texts)
    vocab_size = len(_vocab)

    if vocab_size == 0:
        _tfidf_matrix = None
        return

    df = np.zeros(vocab_size, dtype=np.float32)
    for text in texts:
        seen = set()
        for g in _char_ngrams(text, 2) + _char_ngrams(text, 3):
            if g in _vocab and g not in seen:
                df[_vocab[g]] += 1
                seen.add(g)

    n_docs = len(texts)
    _idf = np.log((n_docs + 1) / (df + 1)) + 1.0

    matrix = np.zeros((n_docs, vocab_size), dtype=np.float32)
    for i, text in enumerate(texts):
        matrix[i] = _text_to_tfidf(text, _vocab, _idf)

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    _tfidf_matrix = matrix / norms

    logger.info(f"TF-IDF索引构建完成: {n_docs}个文档块, {vocab_size}维特征")


def _build_embedding_index() -> None:
    """构建Embedding索引矩阵。"""
    global _embedding_matrix

    if not _chunk_id_list:
        _embedding_matrix = None
        return

    texts = [_chunks_db[cid].content for cid in _chunk_id_list]

    try:
        embeddings = embedding_service.encode_texts(texts, dim=128)

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        _embedding_matrix = embeddings / norms

        logger.info(f"Embedding索引构建完成: {len(texts)}个文档块, 128维特征")
    except Exception as e:
        logger.warning(f"Embedding索引构建失败: {e}")
        _embedding_matrix = None


def _build_index() -> None:
    """构建所有索引（TF-IDF + Embedding）。"""
    _build_tfidf_index()
    if USE_HYBRID_RETRIEVAL:
        _build_embedding_index()


def add_textbook_chunks(textbook_id: str, textbook_name: str, chapters: list) -> None:
    """添加教材章节的文档块到索引。

    Args:
        textbook_id: 教材ID。
        textbook_name: 教材名称。
        chapters: 章节列表。
    """
    new_chunks = []
    for ch in chapters:
        texts = split_chunks(ch.content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        for t in texts:
            new_chunks.append(Chunk(
                id=gen_id(),
                textbook_id=textbook_id,
                textbook_name=textbook_name,
                chapter_id=ch.id,
                chapter_title=ch.title,
                content=t,
                page=getattr(ch, 'page_start', 0),
            ))

    if not new_chunks:
        return

    for chunk in new_chunks:
        _chunks_db[chunk.id] = chunk
        _chunk_id_list.append(chunk.id)

    _build_index()
    logger.info(f"已添加 {len(new_chunks)} 个文档块 (来自 {textbook_name})")


def _retrieve_bm25(question: str, top_k: int = 5, textbook_filter: str | None = None) -> list[tuple[str, float]]:
    """BM25检索（基于TF-IDF余弦相似度）。

    Args:
        question: 查询问题。
        top_k: 返回结果数量。
        textbook_filter: 教材ID过滤条件。

    Returns:
        (chunk_id, score) 列表。
    """
    if _tfidf_matrix is None or _vocab is None or _idf is None:
        return []

    q_vec = _text_to_tfidf(question, _vocab, _idf)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_vec = q_vec / q_norm

    sims = _tfidf_matrix @ q_vec

    results = []
    for idx in np.argsort(sims)[::-1]:
        if idx < 0 or idx >= len(_chunk_id_list):
            continue
        score = float(sims[idx])
        if score < 0.01:
            break
        chunk_id = _chunk_id_list[idx]
        chunk = _chunks_db.get(chunk_id)
        if chunk is None:
            continue
        if textbook_filter and chunk.textbook_id != textbook_filter:
            continue
        results.append((chunk_id, score))
        if len(results) >= top_k * 2:
            break
    return results


def _retrieve_embedding(question: str, top_k: int = 5, textbook_filter: str | None = None) -> list[tuple[str, float]]:
    """Embedding检索（基于余弦相似度）。

    Args:
        question: 查询问题。
        top_k: 返回结果数量。
        textbook_filter: 教材ID过滤条件。

    Returns:
        (chunk_id, score) 列表。
    """
    if _embedding_matrix is None:
        return []

    try:
        q_vec = embedding_service.encode_single(question, dim=128)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_vec = q_vec / q_norm

        sims = (_embedding_matrix @ q_vec.T).flatten()

        results = []
        for idx in np.argsort(sims)[::-1]:
            if idx < 0 or idx >= len(_chunk_id_list):
                continue
            score = float(sims[idx])
            if score < 0.01:
                break
            chunk_id = _chunk_id_list[idx]
            chunk = _chunks_db.get(chunk_id)
            if chunk is None:
                continue
            if textbook_filter and chunk.textbook_id != textbook_filter:
                continue
            results.append((chunk_id, score))
            if len(results) >= top_k * 2:
                break
        return results
    except Exception as e:
        logger.warning(f"Embedding检索失败: {e}")
        return []


def _fuse_results(
    bm25_results: list[tuple[str, float]],
    embed_results: list[tuple[str, float]],
    top_k: int,
) -> list[tuple[str, float]]:
    """融合BM25和Embedding检索结果。

    Args:
        bm25_results: BM25检索结果。
        embed_results: Embedding检索结果。
        top_k: 返回结果数量。

    Returns:
        融合后的 (chunk_id, score) 列表。
    """
    scores: dict[str, float] = {}

    if bm25_results:
        max_bm25 = max(s for _, s in bm25_results) if bm25_results else 1.0
        max_bm25 = max(max_bm25, 0.001)
        for chunk_id, score in bm25_results:
            normalized = score / max_bm25
            scores[chunk_id] = scores.get(chunk_id, 0) + BM25_WEIGHT * normalized

    if embed_results:
        max_embed = max(s for _, s in embed_results) if embed_results else 1.0
        max_embed = max(max_embed, 0.001)
        for chunk_id, score in embed_results:
            normalized = score / max_embed
            scores[chunk_id] = scores.get(chunk_id, 0) + EMBED_WEIGHT * normalized

    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:top_k]


def retrieve(question: str, top_k: int = 5, textbook_filter: str | None = None) -> list[tuple[Chunk, float]]:
    """检索与问题相关的文档块。

    Args:
        question: 查询问题。
        top_k: 返回结果数量。
        textbook_filter: 教材ID过滤条件。

    Returns:
        (Chunk, score) 列表。
    """
    if USE_HYBRID_RETRIEVAL and _embedding_matrix is not None:
        bm25_results = _retrieve_bm25(question, top_k, textbook_filter)
        embed_results = _retrieve_embedding(question, top_k, textbook_filter)
        fused = _fuse_results(bm25_results, embed_results, top_k)
        results = []
        for chunk_id, score in fused:
            chunk = _chunks_db.get(chunk_id)
            if chunk:
                results.append((chunk, score))
        return results
    else:
        bm25_results = _retrieve_bm25(question, top_k, textbook_filter)
        results = []
        for chunk_id, score in bm25_results:
            chunk = _chunks_db.get(chunk_id)
            if chunk:
                results.append((chunk, score))
        return results


def get_all_chunks() -> list[Chunk]:
    """获取所有文档块。

    Returns:
        文档块列表。
    """
    return list(_chunks_db.values())


def get_chunks_by_textbook(textbook_id: str) -> list[Chunk]:
    """获取指定教材的所有文档块。

    Args:
        textbook_id: 教材ID。

    Returns:
        文档块列表。
    """
    return [c for c in _chunks_db.values() if c.textbook_id == textbook_id]


def get_chunk_count() -> int:
    """获取文档块总数。

    Returns:
        文档块数量。
    """
    return len(_chunks_db)


def get_index_stats() -> dict:
    """获取索引统计信息。

    Returns:
        包含索引配置和状态的字典。
    """
    return {
        "total_chunks": len(_chunks_db),
        "tfidf_enabled": _tfidf_matrix is not None,
        "embedding_enabled": _embedding_matrix is not None,
        "hybrid_retrieval": USE_HYBRID_RETRIEVAL,
        "bm25_weight": BM25_WEIGHT,
        "embed_weight": EMBED_WEIGHT,
    }


def clear_all() -> None:
    """清空所有索引和文档块数据。"""
    global _tfidf_matrix, _embedding_matrix, _chunks_db, _chunk_id_list, _vocab, _idf
    _tfidf_matrix = None
    _embedding_matrix = None
    _chunks_db = {}
    _chunk_id_list = []
    _vocab = {}
    _idf = None
