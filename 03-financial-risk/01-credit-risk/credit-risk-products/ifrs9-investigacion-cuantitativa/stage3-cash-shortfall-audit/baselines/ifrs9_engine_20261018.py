"""Laboratorio IFRS 9 reproducible con datos sintéticos, no productivo."""
from __future__ import annotations

import numpy as np
import pandas as pd


def cartera_sintetica(n: int = 2_000, semilla: int = 91) -> pd.DataFrame:
    """Crea una cartera de ejemplo con información disponible al cierre."""
    rng = np.random.default_rng(semilla)
    score = rng.normal(0, 1, n)
    macro = rng.normal(0, 1, n)
    pd_12m = 1 / (1 + np.exp(-(-2.8 - 0.9 * score + 0.35 * macro)))
    return pd.DataFrame({
        "loan_id": np.arange(1, n + 1), "score": score, "macro": macro,
        "pd_12m": pd_12m.clip(0.001, 0.45),
        "pd_origen": (pd_12m * rng.uniform(.55, .9, n)).clip(.001, .4),
        "dpd": rng.choice([0, 15, 35, 95], n, p=[.78, .12, .07, .03]),
        "ead": rng.lognormal(10.7, .7, n),
        "lgd_base": rng.beta(3, 4, n),
        "ccf": rng.uniform(.2, .85, n), "undrawn": rng.lognormal(9.5, .8, n),
    })


def stage(pd_actual: pd.Series, pd_origen: pd.Series, dpd: pd.Series, umbral_sicr: float = 2.0) -> pd.Series:
    """Staging ilustrativo: Stage 3 por 90+ DPD, Stage 2 por SICR o 30+ DPD."""
    ratio = pd_actual / pd_origen.clip(lower=1e-6)
    return pd.Series(np.select([dpd >= 90, (dpd >= 30) | (ratio >= umbral_sicr)], [3, 2], default=1), index=pd_actual.index)


def pd_lifetime(pd_12m: pd.Series, horizonte: int = 5, crecimiento_hazard: float = .10) -> np.ndarray:
    """Convierte PD 12m en curva marginal anual y acumulada de supervivencia."""
    hazard0 = -np.log1p(-np.asarray(pd_12m))
    hazards = np.stack([hazard0 * (1 + crecimiento_hazard) ** year for year in range(horizonte)], axis=1)
    survival_start = np.concatenate([np.ones((len(pd_12m), 1)), np.exp(-np.cumsum(hazards[:, :-1], axis=1))], axis=1)
    return 1 - np.exp(-hazards) * 1, survival_start * (1 - np.exp(-hazards))


def ecl_componentes(cartera: pd.DataFrame, escenario: str = "base", horizonte: int = 5, tasa_descuento: float = .10) -> pd.DataFrame:
    """Calcula ECL con PD marginal, LGD ajustada por escenario y EAD con CCF."""
    shocks = {"base": (1.0, 1.0), "adverso": (1.45, 1.18), "severo": (2.10, 1.35)}
    if escenario not in shocks:
        raise ValueError("escenario debe ser base, adverso o severo")
    pd_mult, lgd_mult = shocks[escenario]
    out = cartera.copy()
    out["stage"] = stage(out.pd_12m, out.pd_origen, out.dpd)
    _, pd_marginal = pd_lifetime((out.pd_12m * pd_mult).clip(upper=.95), horizonte)
    lgd = (out.lgd_base * lgd_mult).clip(upper=.95).to_numpy()
    ead = (out.ead + out.ccf * out.undrawn).to_numpy()
    descuento = 1 / (1 + tasa_descuento) ** np.arange(1, horizonte + 1)
    ecl_12m = pd_marginal[:, 0] * descuento[0] * lgd * ead
    ecl_lifetime = (pd_marginal * descuento).sum(axis=1) * lgd * ead
    out["ecl_12m"], out["ecl_lifetime"] = ecl_12m, ecl_lifetime
    out["ecl"] = np.where(out.stage.eq(1), out.ecl_12m, out.ecl_lifetime)
    out["escenario"] = escenario
    return out


def ponderar_escenarios(cartera: pd.DataFrame, pesos: dict[str, float]) -> pd.DataFrame:
    if not np.isclose(sum(pesos.values()), 1.0):
        raise ValueError("los pesos de escenario deben sumar 1")
    piezas = [ecl_componentes(cartera, nombre)[["loan_id", "ecl"]].rename(columns={"ecl": nombre}) for nombre in pesos]
    resultado = piezas[0]
    for pieza in piezas[1:]:
        resultado = resultado.merge(pieza, on="loan_id", validate="one_to_one")
    resultado["ecl_ponderada"] = sum(resultado[nombre] * peso for nombre, peso in pesos.items())
    return resultado


def backtest_pd(pd_estimado: pd.Series, default_observado: pd.Series, grupos: int = 10) -> pd.DataFrame:
    """Tabla de calibración OOT por cuantiles; no sustituye validación independiente."""
    frame = pd.DataFrame({"pd": pd_estimado, "default": default_observado})
    frame["banda"] = pd.qcut(frame.pd.rank(method="first"), grupos, labels=False)
    resumen = frame.groupby("banda", observed=True).agg(cuentas=("default", "size"), pd_media=("pd", "mean"), default_observado=("default", "mean"))
    resumen["error_calibracion"] = resumen.default_observado - resumen.pd_media
    return resumen
