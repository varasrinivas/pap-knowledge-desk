"""Stage 4, EMBED: text -> 384 numbers, on the CPU, no key.

Model: BAAI/bge-small-en-v1.5 through fastembed (ONNX). Vectors come back unit-length (norm 1.0), so cosine similarity and
dot product are the same number, which is why the collections use the cosine space.

Queries and documents are embedded differently. bge was trained with an instruction in front of short queries
("Represent this sentence for searching relevant passages: "). fastembed's query_embed does NOT add it for this model
(measured: identical vectors), so we add it ourselves, to queries only, never to documents.
"""
from __future__ import annotations

import time
from functools import lru_cache

import numpy as np

from desk import config

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class Embedder:
    def __init__(self, model: str = config.EMBED_MODEL):
        from fastembed import TextEmbedding
        self.name = model
        self.model = TextEmbedding(model, cache_dir=str(config.MODEL_CACHE))
        self.tokenizer = self.model.model.tokenizer          # the model's own WordPiece tokenizer (truncates at 512)

    def docs(self, texts: list[str], batch_size: int = config.EMBED_BATCH) -> np.ndarray:
        return np.array(list(self.model.embed(texts, batch_size=batch_size)), dtype=np.float32)

    def query(self, text: str, prefix: bool = True) -> np.ndarray:
        return np.array(next(self.model.embed([(QUERY_PREFIX if prefix else "") + text])), dtype=np.float32)


@lru_cache(maxsize=1)
def embedder() -> Embedder:
    return Embedder()


def benchmark(texts: list[str], sizes=(16, 64, 256)) -> list[dict]:
    """Batch size vs throughput on this machine (docs/second)."""
    e, out = embedder(), []
    for b in sizes:
        t0 = time.time()
        e.docs(texts, batch_size=b)
        dt = time.time() - t0
        out.append({"batch_size": b, "docs": len(texts), "seconds": round(dt, 2), "docs_per_s": round(len(texts) / dt, 1)})
    return out
