from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("KV_DATA_DIR", PROJECT_ROOT / "data"))
    db_dir: Path = Path(os.getenv("KV_DB_DIR", PROJECT_ROOT / "vault_db"))
    collection_name: str = os.getenv("KV_COLLECTION", "knowledge_vault")
    embedding_backend: str = os.getenv("KV_EMBEDDING_BACKEND", "local")
    sentence_model: str = os.getenv("KV_SENTENCE_MODEL", "all-MiniLM-L6-v2")
    report_backend: str = os.getenv("KV_REPORT_BACKEND", "auto")
    ollama_base_url: str = os.getenv("KV_OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("KV_OLLAMA_MODEL", "qwen3:0.6b")
    ollama_embed_model: str = os.getenv("KV_OLLAMA_EMBED_MODEL", "nomic-embed-text")
    chunk_size: int = int(os.getenv("KV_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("KV_CHUNK_OVERLAP", "150"))
    search_results: int = int(os.getenv("KV_SEARCH_RESULTS", "8"))


settings = Settings()
