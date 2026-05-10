import uuid
import re
import hashlib


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


def calc_checksum(data: bytes) -> str:
    """计算数据的MD5校验和。"""
    return hashlib.md5(data).hexdigest()[:16]


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_chunks(text: str, chunk_size: int = 600, overlap: int = 80) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def truncate(text: str, max_len: int = 200) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text
