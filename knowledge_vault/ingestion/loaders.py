from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import docx2txt
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md", ".markdown"}


@dataclass(frozen=True)
class Document:
    path: Path
    text: str
    metadata: dict[str, str | int]


def discover_files(data_dir: Path) -> list[Path]:
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return sorted(
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def load_document(path: Path, data_dir: Path) -> Document:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".docx":
        text = docx2txt.process(str(path)) or ""
    elif suffix in {".txt", ".md", ".markdown"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".csv":
        text = _read_csv(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    stat = path.stat()
    metadata: dict[str, str | int] = {
        "source": str(path.relative_to(data_dir)),
        "file_name": path.name,
        "extension": suffix,
        "size_bytes": stat.st_size,
        "modified_time": int(stat.st_mtime),
    }
    return Document(path=path, text=_clean_text(text), metadata=metadata)


def load_documents(data_dir: Path) -> list[Document]:
    return [load_document(path, data_dir) for path in discover_files(data_dir)]


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {page_number}]\n{text}")
    return "\n\n".join(pages)


def _read_csv(path: Path) -> str:
    rows: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            for index, row in enumerate(reader, start=1):
                values = "; ".join(f"{key}: {value}" for key, value in row.items())
                rows.append(f"Row {index}: {values}")
        else:
            handle.seek(0)
            plain_reader = csv.reader(handle)
            for index, row in enumerate(plain_reader, start=1):
                rows.append(f"Row {index}: " + "; ".join(row))
    return "\n".join(rows)


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)

