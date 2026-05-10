import os
from ..models.schemas import TextbookMeta, Chapter
from ..parsers.pdf_parser import parse_pdf
from ..parsers.docx_parser import parse_docx
from ..parsers.md_parser import parse_md
from ..parsers.txt_parser import parse_txt
from ..utils.text_utils import gen_id


def parse_textbook(file_path: str, filename: str) -> tuple[TextbookMeta, list[Chapter]]:
    ext = os.path.splitext(filename)[1].lower()
    textbook_id = gen_id()
    textbook_name = os.path.splitext(filename)[0]

    parser_map = {
        '.pdf': parse_pdf,
        '.docx': parse_docx,
        '.md': parse_md,
        '.txt': parse_txt,
    }

    parser = parser_map.get(ext)
    if not parser:
        raise ValueError(f"不支持的文件格式: {ext}")

    chapters = parser(file_path, textbook_id, textbook_name)
    meta = TextbookMeta(
        id=textbook_id,
        filename=filename,
        format=ext.lstrip('.'),
        chapter_count=len(chapters),
    )
    return meta, chapters
