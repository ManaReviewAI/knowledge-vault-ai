from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from knowledge_vault.config.settings import Settings


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalHashEmbedder:
    """Small deterministic embedder that works offline with no model download."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"\w+", text.lower(), flags=re.UNICODE):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "The sentence-transformers backend is optional. "
                "Install it with: pip install -e .[ml]"
            ) from error
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


class OllamaEmbedder:
    def __init__(self, model_name: str, base_url: str) -> None:
        try:
            import ollama
        except ImportError as error:
            raise RuntimeError(
                "The Ollama embedding backend is optional. "
                "Install it with: pip install -e .[ollama]"
            ) from error
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
    if backend == "local":
        return LocalHashEmbedder()
    if backend == "ollama":
        return OllamaEmbedder(settings.ollama_embed_model, settings.ollama_base_url)
    if backend == "sentence_transformers":
        return SentenceTransformersEmbedder(settings.sentence_model)
    raise ValueError(f"Unknown embedding backend: {settings.embedding_backend}")
