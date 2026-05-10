import os
import math
import logging
import numpy as np
from ..models.schemas import Chunk, QAReference
from ..config import settings
from ..utils.text_utils import gen_id, split_chunks

logger = logging.getLogger(__name__)

_chunks_db: dict[str, Chunk] = {}
_chunk_id_list: list[str] = []
_tfidf_matrix: np.ndarray | None = None
_vocab: dict[str, int] = {}
_idf: np.ndarray | None = None


def _char_ngrams(text: str, n: int = 2) -> list[str]:
    text = text.replace('\n', ' ').replace('\r', ' ')
    return [text[i:i+n] for i in range(len(text) - n + 1)]


def _build_vocab(texts: list[str]) -> dict[str, int]:
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
    tf = np.zeros(len(vocab), dtype=np.float32)
    grams = _char_ngrams(text, 2) + _char_ngrams(text, 3)
    for g in grams:
        if g in vocab:
            tf[vocab[g]] += 1
    total = len(grams) if grams else 1
    tf = tf / total
    return tf * idf


def _build_tfidf_index():
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

    logger.info(f"RAG索引构建完成: {n_docs}个文档块, {vocab_size}维特征")


def add_textbook_chunks(textbook_id: str, textbook_name: str, chapters: list):
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

    _build_tfidf_index()
    logger.info(f"已添加 {len(new_chunks)} 个文档块 (来自 {textbook_name})")


def retrieve(question: str, top_k: int = 5, textbook_filter: str | None = None) -> list[tuple[Chunk, float]]:
    if _tfidf_matrix is None or _vocab is None or _idf is None:
        return []

    q_vec = _text_to_tfidf(question, _vocab, _idf)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_vec = q_vec / q_norm

    sims = _tfidf_matrix @ q_vec

    indices = np.argsort(sims)[::-1]
    results = []
    for idx in indices:
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
        results.append((chunk, score))
        if len(results) >= top_k:
            break
    return results


def get_all_chunks() -> list[Chunk]:
    return list(_chunks_db.values())


def get_chunks_by_textbook(textbook_id: str) -> list[Chunk]:
    return [c for c in _chunks_db.values() if c.textbook_id == textbook_id]


def get_chunk_count() -> int:
    return len(_chunks_db)


def clear_all():
    global _tfidf_matrix, _chunks_db, _chunk_id_list, _vocab, _idf
    _tfidf_matrix = None
    _chunks_db = {}
    _chunk_id_list = []
    _vocab = {}
    _idf = None
