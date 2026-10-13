"""Fusion de rankings y diversificacion."""
from __future__ import annotations
import numpy as np


def rrf(rankings: list[list[int]], k: int = 60, top: int | None = None) -> list[int]:
    """Reciprocal Rank Fusion: score(d) = sum_r 1/(k + rank_r(d)), rank desde 1. Desempate por indice."""
    sc: dict[int, float] = {}
    for r in rankings:
        for pos, d in enumerate(r, 1): sc[d] = sc.get(d, 0.0) + 1.0 / (k + pos)
    out = sorted(sc, key=lambda d: (-sc[d], d)); return out[:top] if top else out


def minmax(x: np.ndarray) -> np.ndarray:
    lo, hi = float(np.min(x)), float(np.max(x)); return np.zeros_like(x, dtype=float) if hi == lo else (x - lo) / (hi - lo)


def weighted(score_vectors: list[np.ndarray], weights: list[float]) -> np.ndarray:
    """Combinacion lineal de puntajes normalizados min-max."""
    return sum(w * minmax(s) for w, s in zip(weights, score_vectors))


def mmr(candidates: list[int], rel: dict[int, float], sim, lam: float = 0.7, k: int = 5) -> list[int]:
    """Maximal Marginal Relevance: lam*rel(d) - (1-lam)*max_{s in S} sim(d, s)."""
    chosen: list[int] = []; pool = list(candidates)
    while pool and len(chosen) < k:
        best = max(pool, key=lambda d: (lam * rel[d] - (1 - lam) * max((sim(d, s) for s in chosen), default=0.0), -d))
        chosen.append(best); pool.remove(best)
    return chosen
