"""Compuertas secuenciales de regresion: SPRT de Wald sobre discordancias pareadas y diseno de tamano fijo."""
from __future__ import annotations
import numpy as np


def sprt_bounds(alpha: float, beta: float):
    """Fronteras de Wald para el log-cociente de verosimilitud: A=ln((1-beta)/alpha) (rechazar H0), B=ln(beta/(1-alpha)) (aceptar H0)."""
    return float(np.log((1 - beta) / alpha)), float(np.log(beta / (1 - alpha)))


def sprt_regression(outcomes: np.ndarray, p0: float = 0.5, p1: float = 0.7, alpha: float = 0.05, beta: float = 0.2, max_pairs: int | None = None):
    """SPRT sobre pares discordantes. outcomes: +1 (nuevo mejora: B acierta, A falla), -1 (empeora), 0 (concordante, se ignora).
    Entre discordantes, la prob. de 'mejora' es p. H0: p=p0 (p. ej. 0.5 = sin cambio) vs H1: p=p1 (hay mejora relevante).
    Para detectar REGRESIONES se invierten los signos antes de llamar. Devuelve ('H1'|'H0'|'continuar', discordantes_usados, pares_vistos)."""
    A, B = sprt_bounds(alpha, beta); llr = 0.0; used = 0
    for t, o in enumerate(outcomes, 1):
        if max_pairs and t > max_pairs: break
        if o == 0: continue
        used += 1; llr += np.log(p1 / p0) if o > 0 else np.log((1 - p1) / (1 - p0))
        if llr >= A: return "H1", used, t
        if llr <= B: return "H0", used, t
    return "continuar", used, t if len(outcomes) else 0


def gate_fixed(outcomes: np.ndarray, alpha: float = 0.05) -> str:
    """Compuerta de tamano fijo: prueba binomial exacta bilateral sobre discordantes; 'H1' si p<alpha y mejora neta > 0."""
    from scipy.stats import binomtest
    o = np.asarray(outcomes); b, c = int((o > 0).sum()), int((o < 0).sum())
    if b + c == 0: return "H0"
    return "H1" if binomtest(b, b + c, 0.5).pvalue < alpha and b > c else "H0"
