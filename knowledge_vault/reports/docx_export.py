from __future__ import annotations

import re
from io import BytesIO

from docx import Document

from knowledge_vault.search.searcher import SearchResult


def build_report_docx(report_markdown: str, results: list[SearchResult]) -> BytesIO:
    document = Document()
    document.add_heading("Knowledge Vault AI Report", level=0)

    for raw_line in report_markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            document.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## "):
            document.add_heading(line[3:].strip(), level=2)
        elif line.startswith("- "):
            document.add_paragraph(line[2:].strip(), style="List Bullet")
        else:
            document.add_paragraph(line)

    document.add_heading("Retrieved Evidence Extracts", level=1)
    for result in results:
        document.add_paragraph(
            f"{result.file_name}, chunk {result.chunk_index}",
            style="List Bullet",
        )
        document.add_paragraph(f"Excerpt: {result.excerpt}")

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


def safe_report_filename(topic: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9]+", "-", topic.strip().lower()).strip("-")
    return f"knowledge-vault-report-{name or 'archive'}.docx"
