from __future__ import annotations

import argparse

from knowledge_vault.config.settings import settings
from knowledge_vault.indexing.embeddings import build_embedder
from knowledge_vault.pipeline import rebuild_index
from knowledge_vault.reports.generator import generate_report
from knowledge_vault.search.searcher import semantic_search


def ingest_main() -> None:
    summary = rebuild_index(settings)
    print(f"Indexed {summary.documents} documents into {summary.chunks} chunks.")


def search_main() -> None:
    parser = argparse.ArgumentParser(description="Search the local Knowledge Vault AI archive.")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=settings.search_results)
    args = parser.parse_args()

    results = semantic_search(args.query, build_embedder(settings), settings, limit=args.limit)
    for result in results:
        print(f"{result.file_name} | chunk {result.chunk_index} | score {result.score:.3f}")
        print(result.excerpt)
        print()


def report_main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local source-grounded report.")
    parser.add_argument("prompt")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    results = semantic_search(args.prompt, build_embedder(settings), settings, limit=args.limit)
    print(generate_report(args.prompt, results, settings))

