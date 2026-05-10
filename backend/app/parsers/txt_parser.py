import re
from ..models.schemas import Chapter
from ..utils.text_utils import gen_id, clean_text


def parse_txt(file_path: str, textbook_id: str, textbook_name: str) -> list[Chapter]:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = text.split('\n')
    chapters: list[Chapter] = []
    current_title = ""
    current_content = ""

    for line in lines:
        stripped = line.strip()
        if _is_heading(stripped):
            if current_content.strip():
                chapters.append(Chapter(
                    id=gen_id(),
                    textbook_id=textbook_id,
                    textbook_name=textbook_name,
                    title=current_title or f"第{len(chapters)+1}章",
                    content=clean_text(current_content),
                ))
            current_title = stripped
            current_content = ""
        else:
            current_content += stripped + "\n"

    if current_content.strip():
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title=current_title or f"第{len(chapters)+1}章",
            content=clean_text(current_content),
        ))

    if not chapters:
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title="全文",
            content=clean_text(text),
        ))
    return chapters


def _is_heading(line: str) -> bool:
    if not line or len(line) > 60:
        return False
    patterns = [
        r'^第[一二三四五六七八九十\d]+[章节篇]',
        r'^Chapter\s+\d+',
        r'^\d+[\.\s]+[A-Z\u4e00-\u9fff]',
    ]
    return any(re.match(p, line) for p in patterns)
