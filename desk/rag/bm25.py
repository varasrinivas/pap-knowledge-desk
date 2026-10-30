"""The keyword half of hybrid search: a small BM25 index per collection, saved next to the Chroma data.

Why keep one: embeddings blur exact tokens (PI-DOC-004, CR-ND-009, RR-0412, '25 MB'); BM25 matches them exactly.
"""
from __future__ import annotations

import math
import pickle
import re
from collections import Counter

from desk import config

STOP = set("a an and are as at be but by can do does for from has have how i if in into is it its me my no not of on or our "
           "so that the their them then there these they this to was we what when where which who why will with you your".split())
TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    toks = TOKEN.findall(text.lower())
    out = [t for t in toks if t not in STOP]
    for t in toks:                                          # also index the parts of hyphenated codes: pi-doc-004 -> 004
        if "-" in t:
            out += [p for p in t.split("-") if p not in STOP]
    return out


class BM25:
    def __init__(self, ids: list[str], texts: list[str], k1: float = 1.4, b: float = 0.75):
        self.ids, self.k1, self.b = ids, k1, b
        self.docs = [Counter(tokenize(t)) for t in texts]
        self.lens = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lens) / max(1, len(self.lens))
        df = Counter(w for d in self.docs for w in d)
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def search(self, query: str, k: int = 10, allowed: set[str] | None = None) -> list[tuple[str, float]]:
        q = tokenize(query)
        scores = []
        for i, d in enumerate(self.docs):
            if allowed is not None and self.ids[i] not in allowed:
                continue
            s = 0.0
            for w in q:
                f = d.get(w)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg))
            if s > 0:
                scores.append((self.ids[i], s))
        return sorted(scores, key=lambda x: -x[1])[:k]


def path(collection: str):
    return config.RUNTIME_DIR / f"bm25_{collection}.pkl"


def save(collection: str, ids: list[str], texts: list[str]) -> BM25:
    idx = BM25(ids, texts)
    path(collection).write_bytes(pickle.dumps(idx))
    return idx


_cache: dict[str, tuple[float, BM25]] = {}


def load(collection: str) -> BM25 | None:
    p = path(collection)
    if not p.exists():
        return None
    mt = p.stat().st_mtime
    if collection not in _cache or _cache[collection][0] != mt:
        _cache[collection] = (mt, pickle.loads(p.read_bytes()))
    return _cache[collection][1]
