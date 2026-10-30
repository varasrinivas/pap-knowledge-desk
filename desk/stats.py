"""Small, dependency-free statistics used by every eval (ported from the course simulator's sim/agent/rubric.py)."""
from __future__ import annotations

import random
from collections import Counter


def bootstrap_ci(values: list[float], n: int = 2000, alpha: float = 0.05, seed: int = 2026) -> tuple[float, float]:
    """Percentile bootstrap interval for the mean. Small samples give wide intervals; that width is the honest answer."""
    if not values:
        return (float("nan"), float("nan"))
    rnd = random.Random(seed)
    means = sorted(sum(rnd.choice(values) for _ in values) / len(values) for _ in range(n))
    return (round(means[int(n * alpha / 2)], 3), round(means[int(n * (1 - alpha / 2)) - 1], 3))


def cohen_kappa(a: list, b: list) -> float:
    """Unweighted agreement beyond chance between two labellers over the same items."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return 1.0 if pe == 1 else round((po - pe) / (1 - pe), 3)


def macro_f1(gold: list[str], pred: list[str]) -> tuple[float, dict[str, dict]]:
    labels = sorted(set(gold) | set(pred))
    per = {}
    for lab in labels:
        tp = sum(g == lab and p == lab for g, p in zip(gold, pred))
        fp = sum(g != lab and p == lab for g, p in zip(gold, pred))
        fn = sum(g == lab and p != lab for g, p in zip(gold, pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[lab] = {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3), "support": sum(g == lab for g in gold)}
    return round(sum(v["f1"] for v in per.values()) / len(per), 3), per


def confusion(gold: list[str], pred: list[str]) -> tuple[list[str], list[list[int]]]:
    labels = sorted(set(gold) | set(pred))
    idx = {l: i for i, l in enumerate(labels)}
    m = [[0] * len(labels) for _ in labels]
    for g, p in zip(gold, pred):
        m[idx[g]][idx[p]] += 1
    return labels, m
