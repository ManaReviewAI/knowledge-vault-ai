from __future__ import annotations

from dataclasses import dataclass

from knowledge_vault.config.settings import Settings
from knowledge_vault.indexing.embeddings import Embedder
from knowledge_vault.indexing.vector_store import get_collection


@dataclass(frozen=True)
class SearchResult:
    source: str
    file_name: str
    chunk_index: int
    excerpt: str
    score: float


def semantic_search(
    query: str,
    embedder: Embedder,
    settings: Settings,
    limit: int | None = None,
) -> list[SearchResult]:
    collection = get_collection(settings)
    if collection.count() == 0:
        return []

    query_embedding = embedder.embed([query])[0]
    result_limit = limit or settings.search_results
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=result_limit,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output: list[SearchResult] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        score = 1 / (1 + float(distance))
        output.append(
            SearchResult(
                source=str(metadata.get("source", "")),
                file_name=str(metadata.get("file_name", "")),
                chunk_index=int(metadata.get("chunk_index", 0)),
                excerpt=_excerpt(document),
                score=score,
            )
        )
    return output


def format_citations(results: list[SearchResult]) -> str:
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"[{index}] {result.file_name}, chunk {result.chunk_index}: "
            f"\"{result.excerpt}\""
        )
    return "\n".join(lines)


def _excerpt(text: str, max_chars: int = 700) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
