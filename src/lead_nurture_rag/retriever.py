from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import KnowledgeChunk, SearchHit


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_words: int = 120, overlap_words: int = 24) -> list[str]:
    words = normalize_text(text).split()
    if not words:
        return []
    chunks = []
    step = max(1, chunk_words - overlap_words)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_words])
        if chunk:
            chunks.append(chunk)
        if start + chunk_words >= len(words):
            break
    return chunks


def stable_chunk_id(source: str, text: str) -> str:
    digest = hashlib.sha256(f"{source}::{normalize_text(text).lower()}".encode()).hexdigest()[:16]
    return f"chunk_{digest}"


class KnowledgeBase:
    """Small local RAG store using TF-IDF retrieval.

    This keeps the prototype dependency-light and rebuildable. The interface can later be
    swapped for Chroma/Qdrant/OpenAI embeddings without changing the agent loop.
    """

    def __init__(self, persist_path: str | Path | None = None):
        self.persist_path = Path(persist_path) if persist_path else None
        self.chunks: dict[str, KnowledgeChunk] = {}
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        if self.persist_path and self.persist_path.exists():
            self.load()

    def add_text(self, source: str, text: str) -> list[str]:
        ids = []
        for chunk in chunk_text(text):
            chunk_id = stable_chunk_id(source, chunk)
            ids.append(chunk_id)
            self.chunks.setdefault(chunk_id, KnowledgeChunk(id=chunk_id, source=source, text=chunk))
        self._reindex()
        if self.persist_path:
            self.save()
        return ids

    def add_url(self, url: str, timeout: int = 20) -> list[str]:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "lead-nurture-rag-bot/0.1"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        text = f"{title}\n" + soup.get_text(" ")
        return self.add_text(source=url, text=text)

    def search(self, query: str, k: int = 4) -> list[SearchHit]:
        if not self.chunks or not normalize_text(query):
            return []
        self._reindex()
        assert self._vectorizer is not None and self._matrix is not None
        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix).ravel()
        ordered = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:k]
        chunks = list(self.chunks.values())
        return [
            SearchHit(**chunks[index].model_dump(), score=float(score))
            for index, score in ordered
            if score > 0
        ]

    def _reindex(self) -> None:
        if not self.chunks:
            self._vectorizer = None
            self._matrix = None
            return
        texts = [chunk.text for chunk in self.chunks.values()]
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(texts)

    def save(self) -> None:
        if not self.persist_path:
            return
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [chunk.model_dump() for chunk in self.chunks.values()]
        self.persist_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        assert self.persist_path is not None
        payload = json.loads(self.persist_path.read_text(encoding="utf-8"))
        self.chunks = {item["id"]: KnowledgeChunk(**item) for item in payload}
        self._reindex()
