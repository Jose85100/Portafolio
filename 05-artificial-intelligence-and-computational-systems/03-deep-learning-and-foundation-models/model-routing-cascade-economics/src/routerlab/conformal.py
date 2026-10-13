"""Control conforme del riesgo para una cascada de dos niveles (pequeno -> grande)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .world import World


def losses(df: pd.DataFrame, lam: float, small: str = "small", big: str = "large") -> np.ndarray:
    """Perdida por consulta de aceptar la respuesta pequena cuando conf_small >= lam: 1 si la pequena falla y la grande acierta
    (se pierde calidad respecto de usar siempre el grande), 0 si no. Es no creciente en lam."""
    return ((df[f"conf_{small}"].values >= lam) & (df[f"correct_{small}"].values == 0) & (df[f"correct_{big}"].values == 1)).astype(float)


def _risk_curve(cal: pd.DataFrame, small: str, big: str):
    """Candidatos lam (valores de confianza ordenados, 0 y >1) y riesgo empirico R(lam) = media de L_i(lam), vectorizado."""
    conf = cal[f"conf_{small}"].values; l = ((cal[f"correct_{small}"].values == 0) & (cal[f"correct_{big}"].values == 1)).astype(float)
    cand = np.sort(np.unique(np.r_[conf, 0.0, 1.0 + 1e-9])); o = np.argsort(conf); cs = conf[o]; cum = np.r_[np.cumsum(l[o][::-1])[::-1], 0.0]       # cum[j] = perdidas con conf >= cs[j]
    return cand, cum[np.searchsorted(cs, cand, side="left")] / len(conf)


def calibrate_threshold(cal: pd.DataFrame, eps: float, small: str = "small", big: str = "large") -> float:
    """Menor umbral lam tal que (n/(n+1)) * R_hat(lam) + 1/(n+1) <= eps (cota B=1 de la perdida). Garantia (control conforme del riesgo,
    Angelopoulos et al.): si calibracion y prueba son intercambiables, E[perdida de prueba(lam_hat)] <= eps. Si ningun umbral cumple,
    devuelve +inf (todo se escala al grande). Requiere n >= 1/eps - 1 para que exista un umbral."""
    n = len(cal); cand, R = _risk_curve(cal, small, big); ok = np.nonzero((n / (n + 1)) * R + 1.0 / (n + 1) <= eps)[0]
    return float(cand[ok[0]]) if len(ok) else float("inf")


def naive_threshold(cal: pd.DataFrame, eps: float, small: str = "small", big: str = "large") -> float:
    """Menor umbral con riesgo empirico <= eps, SIN correccion de muestra finita (para contrastar)."""
    cand, R = _risk_curve(cal, small, big); ok = np.nonzero(R <= eps)[0]; return float(cand[ok[0]]) if len(ok) else float("inf")


def accept_rate(df: pd.DataFrame, lam: float, small: str = "small") -> float: return float((df[f"conf_{small}"].values >= lam).mean())


def validate_guarantee(w: World, n_cal: int, n_test: int, eps: float, reps: int, seed: int = 0, conservative: bool = True) -> dict:
    """Repite calibracion/prueba independientes `reps` veces. Devuelve riesgo de prueba medio (debe ser <= eps con conservative=True),
    fraccion de repeticiones con riesgo > eps y tasa media de aceptacion del nivel pequeno (ahorro)."""
    rg = np.random.default_rng(seed); riesgos = []; acc = []
    for _ in range(reps):
        cal = w.sample(n_cal, rg); test = w.sample(n_test, rg)
        if conservative: lam = calibrate_threshold(cal, eps)
        else: lam = naive_threshold(cal, eps)
        riesgos.append(losses(test, lam).mean() if np.isfinite(lam) else 0.0); acc.append(accept_rate(test, lam) if np.isfinite(lam) else 0.0)
    r = np.array(riesgos); return {"risk_mean": float(r.mean()), "violation_frac": float((r > eps).mean()), "accept_mean": float(np.mean(acc))}
