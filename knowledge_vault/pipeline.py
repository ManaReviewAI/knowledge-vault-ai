from __future__ import annotations

from dataclasses import dataclass

from knowledge_vault.config.settings import Settings, settings
from knowledge_vault.indexing.chunker import chunk_documents
from knowledge_vault.indexing.embeddings import build_embedder
from knowledge_vault.indexing.vector_store import index_chunks, reset_index
from knowledge_vault.ingestion.loaders import load_documents


@dataclass(frozen=True)
class IngestSummary:
    documents: int
    chunks: int


def rebuild_index(active_settings: Settings = settings) -> IngestSummary:
    documents = load_documents(active_settings.data_dir)
    chunks = chunk_documents(
        documents,
        chunk_size=active_settings.chunk_size,
        overlap=active_settings.chunk_overlap,
    )
    reset_index(active_settings.db_dir)
    embedder = build_embedder(active_settings)
    indexed = index_chunks(chunks, embedder, active_settings)
    return IngestSummary(documents=len(documents), chunks=indexed)

