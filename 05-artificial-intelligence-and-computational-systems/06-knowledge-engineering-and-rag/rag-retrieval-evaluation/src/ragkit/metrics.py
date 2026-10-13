"""Metricas de recuperacion e inferencia estadistica."""
from __future__ import annotations
import numpy as np


def recall_at_k(rank: int | None, k: int) -> float:
    """`rank` = posicion (desde 1) del primer relevante, o None si no aparece."""
    return float(rank is not None and rank <= k)


def mrr(rank: int | None) -> float:
    return 0.0 if rank is None else 1.0 / rank


def ndcg_at_k(rels: list[float], k: int) -> float:
    """nDCG@k con ganancia 2^rel - 1 y descuento log2(pos+1); rels en el orden devuelto."""
    r = np.asarray(rels[:k], float); dcg = ((2 ** r - 1) / np.log2(np.arange(2, len(r) + 2))).sum()
    ideal = np.sort(np.asarray(rels, float))[::-1][:k]; idcg = ((2 ** ideal - 1) / np.log2(np.arange(2, len(ideal) + 2))).sum()
    return float(dcg / idcg) if idcg > 0 else 0.0


def bootstrap_ci(x, stat=np.mean, B: int = 2000, alpha: float = 0.05, seed: int = 0):
    x = np.asarray(x, float); rg = np.random.default_rng(seed); n = len(x)
    bs = np.array([stat(x[rg.integers(0, n, n)]) for _ in range(B)]); return float(stat(x)), float(np.percentile(bs, 100 * alpha / 2)), float(np.percentile(bs, 100 * (1 - alpha / 2)))


def paired_permutation_test(a, b, B: int = 10000, seed: int = 0) -> float:
    """Prueba de permutacion pareada (cambio de signo) de H0: media(a-b)=0. p-valor bilateral con correccion +1."""
    d = np.asarray(a, float) - np.asarray(b, float); rg = np.random.default_rng(seed); obs = abs(d.mean())
    if obs == 0: return 1.0
    sg = rg.choice([-1.0, 1.0], size=(B, len(d))); return float((1 + (np.abs((sg * d).mean(axis=1)) >= obs - 1e-15).sum()) / (B + 1))


def paired_bootstrap_diff(a, b, B: int = 4000, seed: int = 0):
    d = np.asarray(a, float) - np.asarray(b, float); rg = np.random.default_rng(seed); n = len(d)
    bs = np.array([d[rg.integers(0, n, n)].mean() for _ in range(B)]); return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def required_n(sd_diff: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Tamano de muestra pareado para detectar una diferencia media `delta` con desvio de las diferencias `sd_diff`."""
    from scipy.stats import norm
    return int(np.ceil(((norm.ppf(1 - alpha / 2) + norm.ppf(power)) * sd_diff / delta) ** 2))
