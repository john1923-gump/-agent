import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

_model = None


def _get_char_embedding(text: str, dim: int = 128) -> np.ndarray:
    text = text.lower().strip()
    if not text:
        return np.zeros(dim, dtype=np.float32)

    vec = np.zeros(dim, dtype=np.float32)

    for i, char in enumerate(text[:500]):
        idx = (ord(char) * 7 + i * 3) % dim
        vec[idx] += 1.0

    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        hash_val = sum(ord(c) for c in bigram)
        idx = (hash_val * 11 + i * 5) % dim
        vec[idx] += 0.5

    for i in range(len(text) - 2):
        trigram = text[i:i+3]
        hash_val = sum(ord(c) for c in trigram)
        idx = (hash_val * 13 + i * 7) % dim
        vec[idx] += 0.3

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec


def encode_texts(texts: list[str], dim: int = 128) -> np.ndarray:
    embeddings = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        embeddings[i] = _get_char_embedding(text, dim)
    return embeddings


def encode_single(text: str, dim: int = 128) -> np.ndarray:
    return _get_char_embedding(text, dim).reshape(1, -1)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if vec_a.ndim > 1:
        vec_a = vec_a.flatten()
    if vec_b.ndim > 1:
        vec_b = vec_b.flatten()

    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def compute_similarity_matrix(texts_a: list[str], texts_b: list[str], dim: int = 128) -> np.ndarray:
    embeddings_a = encode_texts(texts_a, dim)
    embeddings_b = encode_texts(texts_b, dim)

    sims = np.zeros((len(texts_a), len(texts_b)), dtype=np.float32)
    for i in range(len(texts_a)):
        for j in range(len(texts_b)):
            sims[i, j] = cosine_similarity(embeddings_a[i], embeddings_b[j])

    return sims


def find_similar_pairs(
    texts: list[str],
    ids: list[str],
    threshold: float = 0.5,
    dim: int = 128,
) -> list[tuple[int, int, float]]:
    embeddings = encode_texts(texts, dim)
    n = len(texts)
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim >= threshold:
                pairs.append((i, j, sim))

    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


def compute_batch_similarity(texts: list[str], dim: int = 128) -> np.ndarray:
    embeddings = encode_texts(texts, dim)
    return np.dot(embeddings, embeddings.T)
