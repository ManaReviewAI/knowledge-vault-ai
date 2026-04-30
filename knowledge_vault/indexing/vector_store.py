from __future__ import annotations

import shutil
from pathlib import Path

import chromadb

from knowledge_vault.config.settings import Settings
from knowledge_vault.indexing.chunker import Chunk
from knowledge_vault.indexing.embeddings import Embedder


def get_collection(settings: Settings):
    client = chromadb.PersistentClient(path=str(settings.db_dir))
    return client.get_or_create_collection(name=settings.collection_name)


def reset_index(db_dir: Path) -> None:
    if db_dir.exists():
        shutil.rmtree(db_dir)


def index_chunks(chunks: list[Chunk], embedder: Embedder, settings: Settings) -> int:
    if not chunks:
        return 0

    settings.db_dir.mkdir(parents=True, exist_ok=True)
    collection = get_collection(settings)

    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed(texts)

    collection.add(
        ids=[chunk.id for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[chunk.metadata for chunk in chunks],
    )
    return len(chunks)

