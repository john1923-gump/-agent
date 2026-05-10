"""解析服务：检测格式并解析各类教材文件。"""
import os
import mimetypes
import logging
from ..models.schemas import Chapter, TextbookFormat, TextbookMeta
from ..utils.text_utils import gen_id

logger = logging.getLogger(__name__)

MAGIC_BYTES = {
    b"%PDF": TextbookFormat.PDF,
    b"PK\x03\x04": TextbookFormat.DOCX,
}

SUPPORTED_EXTS = {".pdf", ".docx", ".md", ".txt"}


def detect_format(file_path: str, filename: str = "") -> tuple[TextbookFormat | None, str | None]:
    """检测文件格式（magic bytes + 扩展名双重检测）。

    Args:
        file_path: 文件路径。
        filename: 原始文件名（可选，用于扩展名检测）。

    Returns:
        (格式, 错误信息) 元组。格式为None时表示检测失败。
    """
    ext = os.path.splitext(filename or file_path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        return None, f"不支持的格式: {ext}。支持: {', '.join(SUPPORTED_EXTS)}"

    try:
        with open(file_path, "rb") as f:
            header = f.read(8)
    except Exception as e:
        return None, f"读取文件失败: {e}"

    fmt_by_ext = {
        ".pdf": TextbookFormat.PDF,
        ".docx": TextbookFormat.DOCX,
        ".md": TextbookFormat.MD,
        ".txt": TextbookFormat.TXT,
    }

    for magic, fmt in MAGIC_BYTES.items():
        if header.startswith(magic):
            expected_fmt = fmt_by_ext.get(ext)
            if expected_fmt == fmt:
                return fmt, None
            elif expected_fmt and ext in (".md", ".txt"):
                logger.warning(f"文件内容是{fmt.value}格式，但扩展名是{ext}，按内容格式处理")
                return fmt, None
            else:
                return fmt, None

    if ext in (".md", ".txt"):
        return fmt_by_ext[ext], None

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        mime_to_fmt = {
            "application/pdf": TextbookFormat.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": TextbookFormat.DOCX,
            "text/markdown": TextbookFormat.MD,
            "text/plain": TextbookFormat.TXT,
        }
        if mime_type in mime_to_fmt:
            return mime_to_fmt[mime_type], None

    return None, f"无法识别文件格式"


def _validate_file(file_path: str, fmt: TextbookFormat) -> str | None:
    """验证文件内容是否与格式匹配。

    Args:
        file_path: 文件路径。
        fmt: 文件格式。

    Returns:
        错误信息，验证通过返回None。
    """
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "文件为空"
        if file_size > 50 * 1024 * 1024:
            return f"文件过大: {file_size / 1024 / 1024:.1f}MB (最大50MB)"

        with open(file_path, "rb") as f:
            header = f.read(4)

        if fmt == TextbookFormat.PDF:
            if not header.startswith(b"%PDF"):
                return "PDF文件头验证失败"
        elif fmt == TextbookFormat.DOCX:
            if not header.startswith(b"PK"):
                return "DOCX文件头验证失败（不是有效的Word文档）"

        return None
    except Exception as e:
        return f"文件验证失败: {e}"


def parse(file_path: str, meta: TextbookMeta) -> tuple[list[Chapter], str | None]:
    """解析教材文件为章节列表。

    Args:
        file_path: 文件路径。
        meta: 教材元数据。

    Returns:
        (章节列表, 错误信息) 元组。
    """
    validation_error = _validate_file(file_path, meta.format)
    if validation_error:
        return [], validation_error

    try:
        if meta.format == TextbookFormat.PDF:
            from ..parsers.pdf_parser import parse_pdf
            chapters = parse_pdf(file_path, meta.id, meta.filename)
        elif meta.format == TextbookFormat.DOCX:
            from ..parsers.docx_parser import parse_docx
            chapters = parse_docx(file_path, meta.id, meta.filename)
        elif meta.format == TextbookFormat.MD:
            from ..parsers.md_parser import parse_md
            chapters = parse_md(file_path, meta.id, meta.filename)
        elif meta.format == TextbookFormat.TXT:
            chapters = _parse_txt(file_path, meta.id, meta.filename)
        else:
            return [], f"不支持的格式: {meta.format}"

        for ch in chapters:
            if not ch.id:
                ch.id = gen_id()

        logger.info(f"解析完成: {meta.filename} -> {len(chapters)} 章节")
        return chapters, None

    except Exception as e:
        error_msg = f"解析失败: {e}"
        logger.error(f"{error_msg} | 提示: 如果是扫描版PDF，请先使用OCR工具转换")
        return [], error_msg


def _parse_txt(file_path: str, textbook_id: str, textbook_name: str) -> list[Chapter]:
    """解析纯文本文件。

    Args:
        file_path: 文件路径。
        textbook_id: 教材ID。
        textbook_name: 教材名称。

    Returns:
        章节列表。
    """
    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
    text = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                text = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if text is None:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

    paragraphs = text.split("\n\n")
    chapters = []
    batch_size = 20

    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i + batch_size]
        content = "\n\n".join(p.strip() for p in batch if p.strip())
        if content:
            chapters.append(Chapter(
                id=gen_id(),
                textbook_id=textbook_id,
                textbook_name=textbook_name,
                title=f"第{i // batch_size + 1}部分",
                content=content,
                page_start=i // batch_size + 1,
                page_end=min(i + batch_size, len(paragraphs)) // batch_size + 1,
            ))

    if not chapters:
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title="全文",
            content=text[:50000],
        ))

    return chapters
