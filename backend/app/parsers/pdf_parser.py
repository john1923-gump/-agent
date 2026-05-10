import fitz
from ..models.schemas import Chapter
from ..utils.text_utils import gen_id, clean_text


def parse_pdf(file_path: str, textbook_id: str, textbook_name: str) -> list[Chapter]:
    doc = fitz.open(file_path)
    chapters: list[Chapter] = []
    current_title = ""
    current_content = ""
    page_start = 1

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            if _is_heading(stripped, page_num):
                if current_content.strip():
                    chapters.append(Chapter(
                        id=gen_id(),
                        textbook_id=textbook_id,
                        textbook_name=textbook_name,
                        title=current_title or f"第{len(chapters)+1}章",
                        content=clean_text(current_content),
                        page_start=page_start,
                        page_end=page_num,
                    ))
                current_title = stripped
                current_content = ""
                page_start = page_num + 1
            else:
                current_content += stripped + "\n"

    if current_content.strip():
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title=current_title or f"第{len(chapters)+1}章",
            content=clean_text(current_content),
            page_start=page_start,
            page_end=len(doc),
        ))

    doc.close()
    if not chapters:
        full_text = ""
        doc2 = fitz.open(file_path)
        for p in doc2:
            full_text += p.get_text()
        doc2.close()
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title="全文",
            content=clean_text(full_text),
            page_start=1,
            page_end=len(doc) if hasattr(doc, '__len__') else 1,
        ))
    return chapters


def _is_heading(line: str, page_num: int) -> bool:
    if not line or len(line) > 60:
        return False
    import re
    patterns = [
        r'^第[一二三四五六七八九十\d]+[章节篇]',
        r'^Chapter\s+\d+',
        r'^\d+[\.\s]+[A-Z\u4e00-\u9fff]',
        r'^[一二三四五六七八九十]+[、.]',
    ]
    return any(re.match(p, line) for p in patterns)
