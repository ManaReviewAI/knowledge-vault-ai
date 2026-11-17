from __future__ import annotations

import unittest
from dataclasses import replace

from knowledge_vault.config.settings import settings
from knowledge_vault.indexing.embeddings import LocalHashEmbedder, build_embedder
from knowledge_vault.reports.generator import generate_report, generate_structured_report
from knowledge_vault.search.searcher import SearchResult


class OfflineDefaultsTest(unittest.TestCase):
    def test_default_embedder_runs_without_optional_models(self) -> None:
        test_settings = replace(settings, embedding_backend="local")
        embedder = build_embedder(test_settings)
        vectors = embedder.embed(["wetland birds", "wetland restoration"])

        self.assertIsInstance(embedder, LocalHashEmbedder)
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 384)
        self.assertAlmostEqual(sum(value * value for value in vectors[0]), 1.0)

    def test_extractive_reports_need_no_ollama_service(self) -> None:
        test_settings = replace(settings, report_backend="extractive")
        results = [
            SearchResult(
                source="notes.md",
                file_name="notes.md",
                chunk_index=1,
                excerpt="Kereru were recorded beside the restored wetland in 2024.",
                score=0.9,
            )
        ]

        freeform = generate_report("Summarise wetland birds", results, test_settings)
        structured = generate_structured_report(
            "Topic: wetland birds",
            results,
            test_settings,
        )

        self.assertIn("notes.md", freeform)
        self.assertIn("Kereru", freeform)
        self.assertIn("Evidence Extracts", structured)


if __name__ == "__main__":
    unittest.main()
