from __future__ import annotations

from typing import Protocol

import ollama
from sentence_transformers import SentenceTransformer

from knowledge_vault.config.settings import Settings


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


class OllamaEmbedder:
    def __init__(self, model_name: str, base_url: str) -> None:
        self.model_name = model_name
        self.client = ollama.Client(host=base_url)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            response = self.client.embeddings(model=self.model_name, prompt=text)
            vectors.append(response["embedding"])
        return vectors


def build_embedder(settings: Settings) -> Embedder:
    backend = settings.embedding_backend.lower().strip()
    if backend == "ollama":
        return OllamaEmbedder(settings.ollama_embed_model, settings.ollama_base_url)
    if backend == "sentence_transformers":
        return SentenceTransformersEmbedder(settings.sentence_model)
    raise ValueError(f"Unknown embedding backend: {settings.embedding_backend}")

