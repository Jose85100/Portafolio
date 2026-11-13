"""¿Raciona crédito el techo de usura? Evidencia con tasas y desembolsos semanales por entidad (SFC, 2007-2022).

Diseño:
  1. Amontonamiento (bunching) de tasas justo debajo del techo: si el techo no restringe, la distribución
     de tasa/techo no debería tener una masa anómala en 0,98-1,00.
  2. Estudio de eventos apilado alrededor de cada recorte del techo de consumo y ordinario. Una celda
     entidad-producto-plazo está "tratada" si su tasa de las cuatro semanas previas supera el nuevo techo:
     está obligada a bajar precio. El grupo de control son celdas del mismo producto que no están
     obligadas. Efectos fijos de celda x evento y de producto x evento x semana relativa.
  3. Placebo con alzas del techo y prueba de tendencias previas.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "03-caso-negocio-credito-digital"))
from caso import usura_semanal  # noqa: E402
from comun import tasas, usura  # noqa: E402

PRODUCTOS = {
    "Tarjeta personas": lambda t: t["tipo"].eq("TARJETAS DE CREDITO PERSONAS NATURALES"),
    "Tarjeta empresarial": lambda t: t["tipo"].eq("TARJETAS DE CREDITO EMPRESARIALES"),
    "Sobregiro": lambda t: t["tipo"].eq("DESCUBIERTOS EN CUENTA CORRIENTE BANCARIA"),
    "Consumo": lambda t: t["modalidad"].eq("CREDITOS DE CONSUMO"),
    "Comercial ordinario": lambda t: t["tipo"].eq("ORDINARIO"),
    "Libranza": lambda t: t["modalidad"].eq("CREDITOS A TRAVES DE LIBRANZA"),
}
MODALIDAD_TECHO = "CONSUMO Y ORDINARIO"


def panel(t: pd.DataFrame | None = None, u: pd.DataFrame | None = None) -> pd.DataFrame:
    t = tasas() if t is None else t
    u = usura() if u is None else u
    inicio = u.loc[u["modalidad"] == MODALIDAD_TECHO, "desde"].min()
    t = t[t["semana"] >= inicio].copy()
    t["producto"] = None
    for k, f in PRODUCTOS.items():
        t.loc[f(t) & t["producto"].isna(), "producto"] = k
    t = t.dropna(subset=["producto"])
    t["techo"] = usura_semanal(u, MODALIDAD_TECHO, t["semana"])
    t["ratio"] = t["tasa_ea"] / t["techo"]
    t["celda"] = t["codigo_entidad"] + "|" + t["producto"] + "|" + t["subcuenta"]
    return t.dropna(subset=["techo"]).reset_index(drop=True)


# ------------------------------------------------------------------ 1. amontonamiento
def amontonamiento(p: pd.DataFrame, producto: str, ancho: float = 0.005, ventana=(0.98, 1.0),
                   rango=(0.80, 1.0), grado: int = 5) -> dict:
    """Masa observada en `ventana` frente a un contrafactual polinómico ajustado fuera de ella
    (Chetty et al., 2011). b = exceso / masa contrafactual promedio por bin de la ventana."""
    x = p.loc[p["producto"] == producto, "ratio"]
    x = x[(x >= rango[0]) & (x < rango[1] + 1e-9)]
    bordes = np.arange(rango[0], rango[1] + ancho / 2, ancho)
    cuenta, _ = np.histogram(x.clip(upper=rango[1] - 1e-9), bins=bordes)
    centro = (bordes[:-1] + bordes[1:]) / 2
    dentro = (centro >= ventana[0]) & (centro < ventana[1])
    coef = np.polyfit(centro[~dentro], cuenta[~dentro], grado)
    contra = np.polyval(coef, centro)
    exceso = cuenta[dentro].sum() - contra[dentro].sum()
    return {"producto": producto, "observaciones": int(len(x)), "exceso": float(exceso),
            "b": float(exceso / contra[dentro].mean()), "razon_masa": float(cuenta[dentro].sum() / contra[dentro].sum()),
            "centro": centro, "cuenta": cuenta, "contrafactual": contra, "ventana": ventana}


def amontonamiento_bootstrap(p: pd.DataFrame, producto: str, n: int = 200, semilla: int = 3) -> tuple[float, float]:
    """Intervalo del cociente observado/contrafactual remuestreando semanas completas (preserva la dependencia
    entre celdas de una misma semana)."""
    rng = np.random.default_rng(semilla)
    x = p[p["producto"] == producto]
    grupos = [g for _, g in x.groupby("semana")]
    vals = []
    for _ in range(n):
        m = pd.concat([grupos[i] for i in rng.integers(0, len(grupos), len(grupos))])
        vals.append(amontonamiento(m, producto)["razon_masa"])
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


# ------------------------------------------------------------------ 2. eventos
def eventos(u: pd.DataFrame | None = None, fin: str = "2022-06-24", minimo_pp: float = 0.25) -> pd.DataFrame:
    u = usura() if u is None else u
    c = u[u["modalidad"] == MODALIDAD_TECHO].sort_values("desde").reset_index(drop=True)
    c["techo_previo"] = c["usura"].shift(1)
    c["cambio_pp"] = c["usura"] - c["techo_previo"]
    c = c.dropna(subset=["cambio_pp"])
    c = c[(c["desde"] <= fin) & (c["cambio_pp"].abs() >= minimo_pp)]
    return c[["desde", "techo_previo", "usura", "cambio_pp"]].rename(columns={"usura": "techo_nuevo"}).reset_index(drop=True)


def apilar(p: pd.DataFrame, ev: pd.DataFrame, productos: list[str], semanas=(-8, 8), definicion=(-12, -9),
           direccion: str = "recorte", umbral: float = 0.99, regla: str = "habitual",
           banda: tuple = (0.90, 0.95)) -> pd.DataFrame:
    """Panel apilado celda x evento x semana relativa.

    regla="habitual" (diseño principal): una celda está tratada si en la ventana de `definicion`, anterior y
    separada de la ventana de estimación, su tasa estuvo en promedio a `umbral` o más del techo vigente:
    opera pegada al techo de forma habitual, así que un recorte la obliga y un alza la libera.
    regla="previa" (primera iteración, se conserva para documentar el sesgo): tratada si la tasa de las
    cuatro semanas previas supera el techo nuevo; selecciona celdas con un alza transitoria de tasa.
    regla="banda" (falsación): tratada si su razón tasa/techo habitual está en `banda`, cerca del techo
    pero sin tocarlo; un recorte pequeño no la obliga, así que no debería haber primera etapa ni efecto."""
    p = p[p["producto"].isin(productos)]
    ev = ev[ev["cambio_pp"] < 0] if direccion == "recorte" else ev[ev["cambio_pp"] > 0]
    sem = np.sort(p["semana"].unique())
    lo = min(semanas[0], definicion[0])
    bloques = []
    for k, e in ev.iterrows():
        i0 = np.searchsorted(sem, np.datetime64(e["desde"]))
        if i0 + lo < 0 or i0 + semanas[1] >= len(sem):
            continue
        rel = {sem[i0 + j]: j for j in range(lo, semanas[1] + 1)}
        b = p[p["semana"].isin(rel)].copy()
        b["rel"] = b["semana"].map(rel)
        if regla in ("habitual", "banda"):
            ref = b[b["rel"].between(*definicion)].groupby("celda")["ratio"].mean()
            trat = ref >= umbral if regla == "habitual" else ref.between(*banda)
            if regla == "banda":  # el control excluye a las celdas pegadas al techo
                ref = ref[ref < umbral]
                trat = trat.loc[ref.index]
            intensidad = trat.astype(float) * abs(e["cambio_pp"])
        else:
            ref = b[b["rel"].between(-4, -1)].groupby("celda")["tasa_ea"].mean()
            trat = ref > e["techo_nuevo"]
            intensidad = (ref - e["techo_nuevo"]).clip(lower=0)
        b = b[b["rel"].between(*semanas)]
        presentes = b.groupby("celda")["rel"].agg(lambda r: (r < 0).any() and (r >= 0).any())
        b = b[b["celda"].map(presentes).fillna(False).astype(bool) & b["celda"].isin(ref.index)]
        b["tratada"] = b["celda"].map(trat).astype(int)
        b["intensidad_pp"] = b["celda"].map(intensidad)
        b["evento"] = k
        b["fecha_evento"] = e["desde"]
        b["cambio_pp"] = e["cambio_pp"]
        bloques.append(b)
    s = pd.concat(bloques, ignore_index=True)
    s["log_monto"] = np.log(s["monto"])
    s["log_n"] = np.log(s["n_creditos"].clip(lower=1))
    s["log_ticket"] = s["log_monto"] - s["log_n"]
    s["celda_evento"] = s["celda"] + "#" + s["evento"].astype(str)
    s["grupo_tiempo"] = s["producto"] + "#" + s["evento"].astype(str) + "#" + s["rel"].astype(str)
    s["entidad"] = s["celda"].str.split("|").str[0]
    return s


def estudio_eventos(s: pd.DataFrame, y: str, base: int = -1, cluster: str = "evento") -> pd.DataFrame:
    """y = a_{celda,evento} + g_{producto,evento,semana} + sum_k b_k 1[tratada] 1[rel=k] + e.
    Errores agrupados por evento (fecha del choque) o por entidad."""
    from linearmodels.iv.absorbing import AbsorbingLS
    d = s.dropna(subset=[y]).copy()
    rels = sorted(d["rel"].unique())
    X = pd.DataFrame({f"k{r}": ((d["rel"] == r) & (d["tratada"] == 1)).astype(float) for r in rels if r != base}, index=d.index)
    absorb = pd.DataFrame({"a": pd.Categorical(d["celda_evento"]), "g": pd.Categorical(d["grupo_tiempo"])}, index=d.index)
    grupos = pd.Categorical(d[cluster]).codes
    r = AbsorbingLS(d[y], X, absorb=absorb).fit(cov_type="clustered", clusters=pd.Series(grupos, index=d.index))
    out = pd.DataFrame({"rel": [int(c[1:]) for c in X.columns], "coef": r.params.values, "se": r.std_errors.values})
    out = pd.concat([out, pd.DataFrame({"rel": [base], "coef": [0.0], "se": [0.0]})]).sort_values("rel").reset_index(drop=True)
    out.attrs["n"] = int(r.nobs)
    return out


def did(s: pd.DataFrame, y: str, cluster: str = "evento", desde: int = 0, hasta: int = 8, continuo: bool = False) -> dict:
    """Efecto promedio post (semanas desde..hasta) frente a pre (-8..-1), con los mismos efectos fijos."""
    from linearmodels.iv.absorbing import AbsorbingLS
    d = s[(s["rel"] < 0) | s["rel"].between(desde, hasta)].dropna(subset=[y]).copy()
    trat = d["intensidad_pp"] if continuo else d["tratada"]
    X = pd.DataFrame({"post_x_trat": ((d["rel"] >= 0).astype(float) * trat)}, index=d.index)
    absorb = pd.DataFrame({"a": pd.Categorical(d["celda_evento"]), "g": pd.Categorical(d["grupo_tiempo"])}, index=d.index)
    r = AbsorbingLS(d[y], X, absorb=absorb).fit(cov_type="clustered", clusters=pd.Series(pd.Categorical(d[cluster]).codes, index=d.index))
    return {"y": y, "coef": float(r.params.iloc[0]), "se": float(r.std_errors.iloc[0]), "t": float(r.tstats.iloc[0]),
            "p": float(r.pvalues.iloc[0]), "n": int(r.nobs), "clusters": int(d[cluster].nunique()),
            "celdas_tratadas": int(d.loc[d["tratada"] == 1, "celda_evento"].nunique()),
            "celdas_control": int(d.loc[d["tratada"] == 0, "celda_evento"].nunique())}


def prueba_tendencias(es: pd.DataFrame) -> dict:
    """Wald conjunto (diagonal, conservador sin covarianzas) de que los coeficientes previos son cero."""
    from scipy import stats
    pre = es[(es["rel"] < -1)]
    chi = float(((pre["coef"] / pre["se"]) ** 2).sum())
    return {"chi2": chi, "gl": int(len(pre)), "p": float(1 - stats.chi2.cdf(chi, len(pre)))}
