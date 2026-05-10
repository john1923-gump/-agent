import re
from typing import List
from uuid import uuid4
from fastapi import UploadFile
from app.models.document import DocumentFormat, DocumentSource, Section, DocumentStructure


async def parse_uploaded_document(file: UploadFile) -> DocumentStructure:
    content = await file.read()
    doc_format = _guess_format(file.filename)
    
    if doc_format == DocumentFormat.pdf:
        raw_text, sections = await _parse_pdf(content, file.filename)
    elif doc_format == DocumentFormat.docx:
        raw_text, sections = await _parse_docx(content, file.filename)
    elif doc_format == DocumentFormat.md:
        raw_text, sections = await _parse_markdown(content)
    else:
        raw_text, sections = await _parse_plaintext(content)
    
    source = DocumentSource(
        id=str(uuid4()),
        name=file.filename,
        format=doc_format,
        path=None,
        metadata={"content_type": file.content_type, "sections_count": len(sections)},
    )
    
    return DocumentStructure(source=source, sections=sections, raw_text=raw_text)


async def _parse_pdf(content: bytes, filename: str) -> tuple[str, List[Section]]:
    try:
        import fitz
    except ImportError:
        return content.decode(errors="ignore"), [
            Section(id=str(uuid4()), title="PDF格式", chapter="未安装PyMuPDF", order=1, text=content.decode(errors="ignore"), page=None)
        ]
    
    doc = fitz.open(stream=content, filetype="pdf")
    sections: List[Section] = []
    raw_text_parts = []
    chapter_num = 0
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        raw_text_parts.append(text)
        
        if text.strip():
            chapter_num += 1
            section = Section(
                id=str(uuid4()),
                title=f"第{page_num}页",
                chapter=f"第{chapter_num}章节",
                order=page_num,
                text=text,
                page=page_num,
            )
            sections.append(section)
    
    doc.close()
    raw_text = "\n".join(raw_text_parts)
    return raw_text, sections


async def _parse_docx(content: bytes, filename: str) -> tuple[str, List[Section]]:
    try:
        from docx import Document
        from io import BytesIO
    except ImportError:
        return content.decode(errors="ignore"), [
            Section(id=str(uuid4()), title="DOCX格式", chapter="未安装python-docx", order=1, text=content.decode(errors="ignore"), page=None)
        ]
    
    doc = Document(BytesIO(content))
    sections: List[Section] = []
    raw_text_parts = []
    current_chapter = ""
    section_order = 0
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        raw_text_parts.append(text)
        
        if para.style.name.startswith("Heading"):
            if section_order > 0:
                section_content = "\n".join(raw_text_parts)
                section = Section(
                    id=str(uuid4()),
                    title=current_chapter,
                    chapter=current_chapter,
                    order=section_order,
                    text=section_content,
                    page=None,
                )
                sections.append(section)
            current_chapter = text
            section_order += 1
            raw_text_parts = [text]
        else:
            raw_text_parts.append(text)
    
    if raw_text_parts and current_chapter:
        section = Section(
            id=str(uuid4()),
            title=current_chapter,
            chapter=current_chapter,
            order=section_order,
            text="\n".join(raw_text_parts),
            page=None,
        )
        sections.append(section)
    
    raw_text = "\n".join([s.text for s in sections])
    return raw_text, sections


async def _parse_markdown(content: bytes) -> tuple[str, List[Section]]:
    text = content.decode(errors="ignore")
    raw_text = text
    sections: List[Section] = []
    
    heading_pattern = r"^(#{1,6})\s+(.+)$"
    lines = text.split("\n")
    
    current_section_lines = []
    current_title = ""
    current_chapter = ""
    section_order = 0
    
    for line in lines:
        match = re.match(heading_pattern, line, re.MULTILINE)
        if match:
            if current_section_lines and current_title:
                section_order += 1
                section = Section(
                    id=str(uuid4()),
                    title=current_title,
                    chapter=current_chapter,
                    order=section_order,
                    text="\n".join(current_section_lines),
                    page=None,
                )
                sections.append(section)
            
            level = len(match.group(1))
            current_title = match.group(2)
            if level == 1:
                current_chapter = current_title
            current_section_lines = [line]
        else:
            if current_title:
                current_section_lines.append(line)
    
    if current_section_lines and current_title:
        section_order += 1
        section = Section(
            id=str(uuid4()),
            title=current_title,
            chapter=current_chapter,
            order=section_order,
            text="\n".join(current_section_lines),
            page=None,
        )
        sections.append(section)
    
    if not sections:
        sections = [Section(id=str(uuid4()), title="Markdown内容", chapter="导入", order=1, text=raw_text, page=None)]
    
    return raw_text, sections


async def _parse_plaintext(content: bytes) -> tuple[str, List[Section]]:
    text = content.decode(errors="ignore")
    raw_text = text
    
    section = Section(
        id=str(uuid4()),
        title="纯文本内容",
        chapter="导入",
        order=1,
        text=text,
        page=None,
    )
    
    return raw_text, [section]


def _guess_format(filename: str) -> DocumentFormat:
    suffix = filename.lower().split(".")[-1]
    if suffix == "pdf":
        return DocumentFormat.pdf
    if suffix == "docx":
        return DocumentFormat.docx
    if suffix in ["md", "markdown"]:
        return DocumentFormat.md
    return DocumentFormat.txt
