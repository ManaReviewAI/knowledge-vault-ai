from __future__ import annotations

from dataclasses import dataclass

from knowledge_vault.ingestion.loaders import Document


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    metadata: dict[str, str | int]


def chunk_document(document: Document, chunk_size: int, overlap: int) -> list[Chunk]:
    words = document.text.split()
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0
    step = max(1, chunk_size - overlap)

    while start < len(words):
        end = min(start + chunk_size, len(words))
        text = " ".join(words[start:end])
        chunk_index += 1
        metadata = dict(document.metadata)
        metadata["chunk_index"] = chunk_index
        metadata["word_start"] = start
        metadata["word_end"] = end
        chunk_id = f"{metadata['source']}::chunk-{chunk_index}"
        chunks.append(Chunk(id=chunk_id, text=text, metadata=metadata))
        if end == len(words):
            break
        start += step

    return chunks


def chunk_documents(documents: list[Document], chunk_size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size=chunk_size, overlap=overlap))
    return chunks

