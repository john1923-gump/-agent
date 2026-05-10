import re
from ..models.schemas import Chapter
from ..utils.text_utils import gen_id, clean_text


def parse_md(file_path: str, textbook_id: str, textbook_name: str) -> list[Chapter]:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = re.split(r'^(#{1,3}\s+.+)$', text, flags=re.MULTILINE)
    chapters: list[Chapter] = []
    current_title = ""
    current_content = ""

    for part in sections:
        part = part.strip()
        if re.match(r'^#{1,3}\s+', part):
            if current_content.strip():
                chapters.append(Chapter(
                    id=gen_id(),
                    textbook_id=textbook_id,
                    textbook_name=textbook_name,
                    title=current_title or f"第{len(chapters)+1}节",
                    content=clean_text(current_content),
                ))
            current_title = re.sub(r'^#+\s*', '', part)
            current_content = ""
        else:
            current_content += part + "\n"

    if current_content.strip():
        chapters.append(Chapter(
            id=gen_id(),
            textbook_id=textbook_id,
            textbook_name=textbook_name,
            title=current_title or f"第{len(chapters)+1}节",
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
