from __future__ import annotations

import math
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge_vault.config.settings import settings
from knowledge_vault.indexing.chunker import chunk_documents
from knowledge_vault.indexing.vector_store import index_chunks
from knowledge_vault.ingestion.loaders import load_documents
from knowledge_vault.search.searcher import semantic_search


class DeterministicEmbedder:
    """Small local embedder for smoke tests only; not used by the app."""

    dimensions = 32

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            vector[hash(token) % self.dimensions] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def main() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        sample_data_dir = Path(__file__).resolve().parents[1] / "sample_data"
        test_settings = replace(
            settings,
            data_dir=sample_data_dir,
            db_dir=Path(temp_dir),
            collection_name="smoke_test",
        )
        documents = load_documents(test_settings.data_dir)
        chunks = chunk_documents(documents, test_settings.chunk_size, test_settings.chunk_overlap)
        indexed = index_chunks(chunks, DeterministicEmbedder(), test_settings)
        results = semantic_search("kereru wetland birds", DeterministicEmbedder(), test_settings, limit=3)

    assert documents, "Expected sample documents to load."
    assert indexed > 0, "Expected chunks to be indexed."
    assert results, "Expected at least one search result."
    print(f"Smoke test passed: {len(documents)} docs, {indexed} chunks, {len(results)} results.")
    print(f"Top source: {results[0].file_name}")


if __name__ == "__main__":
    main()
