"""Estadistica para evaluacion: intervalos, pruebas pareadas, acuerdo, correccion de jueces y pruebas multiples."""
from __future__ import annotations
import numpy as np
from scipy import stats as st


# ---------- intervalos para una proporcion ----------
def wald_ci(k: int, n: int, alpha: float = 0.05):
    p = k / n; z = st.norm.ppf(1 - alpha / 2); h = z * np.sqrt(p * (1 - p) / n); return max(p - h, 0.0), min(p + h, 1.0)


def wilson_ci(k: int, n: int, alpha: float = 0.05):
    """Intervalo de Wilson (score): centro (p + z^2/2n)/(1+z^2/n), semiancho z*sqrt(p(1-p)/n + z^2/4n^2)/(1+z^2/n)."""
    p = k / n; z = st.norm.ppf(1 - alpha / 2); d = 1 + z ** 2 / n; c = (p + z ** 2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d; return c - h, c + h


def clopper_pearson_ci(k: int, n: int, alpha: float = 0.05):
    """Intervalo exacto (garantiza cobertura >= 1-alpha)."""
    lo = 0.0 if k == 0 else st.beta.ppf(alpha / 2, k, n - k + 1); hi = 1.0 if k == n else st.beta.ppf(1 - alpha / 2, k + 1, n - k); return float(lo), float(hi)


# ---------- comparaciones pareadas ----------
def mcnemar_exact(b: int, c: int) -> float:
    """Prueba exacta de McNemar: b = A acierta y B falla; c = A falla y B acierta. Bajo H0 b ~ Bin(b+c, 1/2);
    p bilateral = min(1, 2 * P(X <= min(b, c)))."""
    n = b + c
    return 1.0 if n == 0 else float(min(1.0, 2 * st.binom.cdf(min(b, c), n, 0.5)))


def two_prop_z(k1: int, n1: int, k2: int, n2: int) -> float:
    """Prueba z para dos proporciones independientes (bilateral, varianza combinada)."""
    p = (k1 + k2) / (n1 + n2); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); z = (k1 / n1 - k2 / n2) / se if se > 0 else 0.0; return float(2 * st.norm.sf(abs(z)))


def n_paired_binary(p10: float, p01: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Tamano de muestra pareado (aprox. normal sobre las discordantes): p10, p01 = probabilidades de discordancia en cada sentido."""
    za, zb = st.norm.ppf(1 - alpha / 2), st.norm.ppf(power); d = p10 - p01; s = p10 + p01
    return int(np.ceil((za * np.sqrt(s) + zb * np.sqrt(s - d ** 2)) ** 2 / d ** 2))


def n_two_prop(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Tamano de muestra por grupo para dos proporciones independientes."""
    za, zb = st.norm.ppf(1 - alpha / 2), st.norm.ppf(power); pb = (p1 + p2) / 2
    return int(np.ceil((za * np.sqrt(2 * pb * (1 - pb)) + zb * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2))


def cluster_mean_ci(values: np.ndarray, groups: np.ndarray, alpha: float = 0.05):
    """IC para la media con errores estandar robustos por grupos (promedios por grupo; bootstrap-free): trata cada grupo como una observacion."""
    values = np.asarray(values, float); groups = np.asarray(groups)
    u = np.unique(groups); means = np.array([values[groups == g].mean() for g in u]); w = np.array([(groups == g).sum() for g in u], float)
    m = float(np.average(means, weights=w)); G = len(u); se = np.sqrt(G / (G - 1) * np.sum((w / w.sum()) ** 2 * (means - m) ** 2)); t = st.t.ppf(1 - alpha / 2, G - 1); return m, m - t * se, m + t * se


# ---------- acuerdo entre evaluadores ----------
def cohen_kappa(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b); cats = np.unique(np.r_[a, b]); po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in cats); return 1.0 if pe == 1 else float((po - pe) / (1 - pe))


def fleiss_kappa(counts: np.ndarray) -> float:
    """counts[i, j] = numero de evaluadores que asignaron la categoria j al item i (misma cantidad de evaluadores por item)."""
    counts = np.asarray(counts, float); N, k = counts.shape; n = counts[0].sum()
    P_i = (np.sum(counts ** 2, axis=1) - n) / (n * (n - 1)); P_bar = P_i.mean(); p_j = counts.sum(axis=0) / (N * n); Pe = np.sum(p_j ** 2)
    return float((P_bar - Pe) / (1 - Pe))


def krippendorff_alpha_nominal(ratings: np.ndarray) -> float:
    """alpha de Krippendorff (nominal) con valores faltantes (NaN). ratings: evaluadores x items."""
    R = np.asarray(ratings, float); cats = np.unique(R[~np.isnan(R)]); idx = {c: i for i, c in enumerate(cats)}
    o = np.zeros((len(cats), len(cats)))
    for j in range(R.shape[1]):
        vals = R[~np.isnan(R[:, j]), j]; m = len(vals)
        if m < 2: continue
        for x in range(m):
            for y in range(m):
                if x != y: o[idx[vals[x]], idx[vals[y]]] += 1.0 / (m - 1)
    n_c = o.sum(axis=1); n = n_c.sum()
    if n <= 1: return float("nan")
    Do = (o.sum() - np.trace(o)) / n; De = (n ** 2 - np.sum(n_c ** 2)) / (n * (n - 1))
    return float(1 - Do / De) if De > 0 else 1.0


# ---------- correccion de un juez imperfecto ----------
def rogan_gladen(p_obs: float, tpr: float, tnr: float) -> float:
    """Prevalencia verdadera a partir de la observada con un clasificador de sensibilidad `tpr` y especificidad `tnr`:
    p = (p_obs + tnr - 1) / (tpr + tnr - 1). Se recorta a [0, 1]."""
    return float(np.clip((p_obs + tnr - 1) / (tpr + tnr - 1), 0.0, 1.0))


def ppi_mean(judge_unlabeled: np.ndarray, judge_labeled: np.ndarray, gold_labeled: np.ndarray, alpha: float = 0.05):
    """Inferencia asistida por prediccion (PPI) para una media: theta = mean(juez | sin etiqueta) + mean(oro - juez | etiquetados).
    Insesgado aunque el juez sea sesgado; su varianza usa Var(juez)/N + Var(oro-juez)/n. Devuelve (estimacion, lo, hi)."""
    fu = np.asarray(judge_unlabeled, float); fl = np.asarray(judge_labeled, float); y = np.asarray(gold_labeled, float); N, n = len(fu), len(y)
    rect = y - fl; theta = fu.mean() + rect.mean(); se = np.sqrt(fu.var(ddof=1) / N + rect.var(ddof=1) / n); z = st.norm.ppf(1 - alpha / 2); return float(theta), float(theta - z * se), float(theta + z * se)


# ---------- pruebas multiples ----------
def holm(p) -> np.ndarray:
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for r, i in enumerate(o): run = max(run, min(1.0, (m - r) * p[i])); adj[i] = run
    return adj


def benjamini_hochberg(p) -> np.ndarray:
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)[::-1]; adj = np.empty(m); run = 1.0
    for r, i in enumerate(o): run = min(run, p[i] * m / (m - r)); adj[i] = run
    return adj
