"""Validación independiente del modelo satélite de mora de consumo (proyecto 01).

El validador no confía en las cifras del desarrollador: recalcula la serie desde la capa de datos, reestima,
prueba fuera de muestra contra modelos retadores y somete los supuestos a sensibilidad. Cada prueba devuelve
datos para que el notebook derive el hallazgo y su severidad.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox, het_arch
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import jarque_bera

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "01-riesgo-estres-consumo"))
import estres as E  # noqa: E402
from comun import cartera, expit, logit  # noqa: E402


# ------------------------------------------------------------ 1. replicación de datos
def replicar_icv(c: pd.DataFrame | None = None) -> pd.DataFrame:
    """Recalcula el ICV90 de consumo sin usar el código del desarrollador y lo compara."""
    c = cartera() if c is None else c
    propio = c.query("familia == 'Consumo'").pivot_table(index="mes", values=["mora90", "saldo"], aggfunc="sum")
    propio = propio["mora90"] / propio["saldo"]
    dev = E.series_consumo(c)["icv90"]
    return pd.DataFrame({"validador": propio, "desarrollador": dev, "dif_pb": 1e4 * (propio - dev)})


# ------------------------------------------------------------ 2. pronósticos condicionales
def _pronostico(params: pd.Series, rez: dict, d: pd.DataFrame, origen: str, h: int, con_macro: bool = True) -> pd.Series:
    """Pronóstico dinámico desde `origen` usando la macro efectivamente observada (pronóstico condicional,
    la prueba estándar de un modelo de estrés: ¿si hubiera conocido la macro, habría anticipado la mora?)."""
    idx = list(d.index)
    i0 = idx.index(origen)
    y = d["y"].copy()
    out = {}
    for j in range(1, h + 1):
        i = i0 + j
        if i >= len(idx):
            break
        x = {"const": 1.0, "ylag": y.iloc[i - 1], "covid": float(d["covid"].iloc[i])}
        if con_macro:
            for v in ("tpm", "inflacion", "crec"):
                x[v] = d[v].iloc[i - rez[v]]
        y.iloc[i] = sum(params[k] * x[k] for k in params.index)
        out[idx[i]] = y.iloc[i]
    return pd.Series(expit(pd.Series(out)), name="pronostico")


def retadores(d: pd.DataFrame, fin: str) -> dict:
    """Modelo del desarrollador y tres retadores, todos estimados con datos hasta `fin`."""
    rez = E.rezagos_elegidos(E.seleccionar_rezagos(d, fin=fin))
    dev = E.ajustar(d, rez, fin=fin)
    dd = d.loc[:fin]
    Z = pd.DataFrame({"y": dd["y"], "ylag": dd["y"].shift(1), "covid": dd["covid"]}).dropna()
    ar = sm.OLS(Z["y"], sm.add_constant(Z[["ylag", "covid"]])).fit()
    # Estático: sin persistencia, solo macro (el error típico de un modelo satélite ingenuo).
    Zs = E.matriz(dd, rez).drop(columns="ylag").dropna()
    est = sm.OLS(Zs["y"], sm.add_constant(Zs.drop(columns="y"))).fit()
    return {"rez": rez, "desarrollador": dev.params, "ar1": ar.params, "estatico": est.params}


def pronostico_estatico(params: pd.Series, rez: dict, d: pd.DataFrame, origen: str, h: int) -> pd.Series:
    idx = list(d.index)
    i0 = idx.index(origen)
    out = {}
    for j in range(1, h + 1):
        i = i0 + j
        if i >= len(idx):
            break
        val = params["const"] + params["covid"] * d["covid"].iloc[i]
        for v in ("tpm", "inflacion", "crec"):
            val += params[v] * d[v].iloc[i - rez[v]]
        out[idx[i]] = val
    return pd.Series(expit(pd.Series(out)))


def fuera_de_tiempo(d: pd.DataFrame, fin: str = "2022-06", h: int = 24) -> pd.DataFrame:
    """Estima hasta `fin` (antes del deterioro) y pronostica h meses con macro observada."""
    m = retadores(d, fin)
    obs = d["icv90"]
    f = pd.DataFrame({
        "observado": obs,
        "desarrollador": _pronostico(m["desarrollador"], m["rez"], d, fin, h),
        "ar1": _pronostico(m["ar1"], m["rez"], d, fin, h, con_macro=False),
        "estatico": pronostico_estatico(m["estatico"], m["rez"], d, fin, h),
    }).dropna(subset=["desarrollador"])
    f["paseo_aleatorio"] = obs.loc[fin]
    f.attrs["rez"] = m["rez"]
    return f


def backtest_rodante(d: pd.DataFrame, origenes: list[str], h: int = 12) -> pd.DataFrame:
    """Origen rodante: reestima (incluida la selección de rezagos) en cada origen y mide el error a h meses."""
    filas = []
    for o in origenes:
        m = retadores(d, o)
        preds = {
            "desarrollador": _pronostico(m["desarrollador"], m["rez"], d, o, h),
            "ar1": _pronostico(m["ar1"], m["rez"], d, o, h, con_macro=False),
            "estatico": pronostico_estatico(m["estatico"], m["rez"], d, o, h),
        }
        for nombre, pr in preds.items():
            obs = d["icv90"].reindex(pr.index)
            for k, (mes, v) in enumerate(pr.items(), start=1):
                filas.append({"origen": o, "modelo": nombre, "h": k, "mes": mes, "pred": v, "obs": obs[mes]})
        for k, mes in enumerate(preds["desarrollador"].index, start=1):
            filas.append({"origen": o, "modelo": "paseo_aleatorio", "h": k, "mes": mes,
                          "pred": d["icv90"].loc[o], "obs": d["icv90"].loc[mes]})
    b = pd.DataFrame(filas)
    b["error_pb"] = 1e4 * (b["pred"] - b["obs"])
    return b


def diebold_mariano(e1: np.ndarray, e2: np.ndarray, h: int) -> tuple[float, float]:
    """DM con pérdida cuadrática y varianza HAC de Newey-West con h-1 rezagos. e1: modelo, e2: retador.
    Estadístico negativo: el modelo tiene menor error."""
    from scipy import stats
    dl = e1 ** 2 - e2 ** 2
    n = len(dl)
    dbar = dl.mean()
    g = [np.sum((dl[k:] - dbar) * (dl[:n - k] - dbar)) / n for k in range(h)]
    var = g[0] + 2 * sum((1 - k / h) * g[k] for k in range(1, h))
    dm = dbar / np.sqrt(var / n)
    return float(dm), float(2 * (1 - stats.norm.cdf(abs(dm))))


# ------------------------------------------------------------ 3. estabilidad
def estabilidad_seleccion(d: pd.DataFrame, cortes: list[str]) -> pd.DataFrame:
    filas = []
    for fin in cortes:
        t = E.seleccionar_rezagos(d, fin=fin)
        sin = t.iloc[0]
        con = t[t["signos_ok"]].iloc[0] if t["signos_ok"].any() else None
        filas.append({"fin": fin, "n": int(sin["n"]),
                      "ganador_libre": f"{int(sin.tpm)}/{int(sin.inflacion)}/{int(sin.crec)}",
                      "signos_libre_ok": bool(sin["signos_ok"]),
                      "ganador_restringido": None if con is None else f"{int(con.tpm)}/{int(con.inflacion)}/{int(con.crec)}",
                      "especificaciones_coherentes": int(t["signos_ok"].sum())})
    return pd.DataFrame(filas)


def coeficientes_recursivos(d: pd.DataFrame, rez: dict, cortes: list[str]) -> pd.DataFrame:
    filas = []
    for fin in cortes:
        r = E.ajustar(d, rez, fin=fin).resultado
        filas.append({"fin": fin, **{f"b_{k}": r.params[k] for k in ("ylag", "tpm", "inflacion", "crec")},
                      **{f"p_{k}": r.pvalues[k] for k in ("tpm", "inflacion", "crec")}})
    return pd.DataFrame(filas).set_index("fin")


# ------------------------------------------------------------ 4. diagnóstico
def diagnostico_residuos(sat) -> dict:
    r = sat.resultado
    ols = sm.OLS(r.model.endog, r.model.exog).fit()
    lb = acorr_ljungbox(ols.resid, lags=[6, 12], return_df=True)
    bg = acorr_breusch_godfrey(ols, nlags=6)
    jb = jarque_bera(ols.resid)
    arch = het_arch(ols.resid, nlags=6)
    X = pd.DataFrame(r.model.exog, columns=r.model.exog_names)
    vif = {c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns) if c != "const"}
    return {"ljung_box_p12": float(lb["lb_pvalue"].iloc[-1]), "breusch_godfrey_p": float(bg[1]),
            "jarque_bera_p": float(jb[1]), "arch_p": float(arch[1]), "vif": vif}


# ------------------------------------------------------------ 5. escenarios y supuestos
def severidad_relativa(proy: dict, d: pd.DataFrame) -> pd.DataFrame:
    hist_max = d["icv90"].max()
    return pd.DataFrame({"pico": {k: v.max() for k, v in proy.items()}}).assign(
        maximo_historico=hist_max, mes_max_historico=d["icv90"].idxmax(),
        supera_historia=lambda t: t["pico"] > hist_max)


def sensibilidad_lgd(imp: pd.DataFrame, choques=(-0.15, 0.0, 0.15)) -> pd.DataFrame:
    sev = imp[imp["escenario"] == "Severo"]
    filas = []
    for ch in choques:
        lgd = (sev["lgd"] + ch).clip(0.05, 1.0)
        filas.append({"choque_lgd": ch, "perdida_billones": float(((sev["icv90_pico"] - sev["icv90_actual"]).clip(lower=0)
                                                                     * sev["saldo"] * lgd).sum() / 1e12)})
    return pd.DataFrame(filas)


def sin_tpm(d: pd.DataFrame, rez: dict) -> dict:
    """Reestima sin la TPM: si el pronóstico casi no cambia, el canal de tasa del escenario es nominal."""
    Z = E.matriz(d, rez).drop(columns="tpm").dropna()
    r = sm.OLS(Z["y"], sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    return {"aic_sin_tpm": float(r.aic), "params": r.params}


# ------------------------------------------------------------ 6. retador remediado
def ajustar_remediado(d: pd.DataFrame, rez: dict, fin: str | None = None) -> dict:
    """Relación de niveles con errores AR(1), estimada por GLS iterado (Cochrane-Orcutt).
    La persistencia queda en el error, no en la variable dependiente: el pronóstico converge a la
    relación macro de largo plazo a velocidad phi^h en vez de acumular rezagos de la propia mora."""
    dd = d if fin is None else d.loc[:fin]
    Z = E.matriz(dd, rez).drop(columns="ylag").dropna()
    X = sm.add_constant(Z.drop(columns="y"))
    r = sm.GLSAR(Z["y"], X, rho=1).iterative_fit(maxiter=50)
    phi = float(r.model.rho[0])
    u = float(Z["y"].iloc[-1] - X.iloc[-1] @ r.params)
    return {"params": r.params, "bse": r.bse, "phi": phi, "u_final": u, "fin": Z.index[-1], "rez": rez}


def pronostico_remediado(m: dict, d: pd.DataFrame, futuro: pd.DataFrame | None = None, h: int = 24) -> pd.Series:
    """Si `futuro` es None, usa la macro observada después de m['fin'] (pronóstico condicional);
    si no, la trayectoria del escenario."""
    hist = d[["tpm", "inflacion", "crec", "covid"]].loc[:m["fin"]]
    todo = hist if futuro is None else pd.concat([hist, futuro[["tpm", "inflacion", "crec", "covid"]]])
    if futuro is None:
        todo = d[["tpm", "inflacion", "crec", "covid"]]
    idx = list(todo.index)
    i0 = idx.index(m["fin"])
    p, out = m["params"], {}
    for j in range(1, h + 1):
        i = i0 + j
        if i >= len(idx):
            break
        val = p["const"] + p["covid"] * todo["covid"].iloc[i]
        for v in ("tpm", "inflacion", "crec"):
            val += p[v] * todo[v].iloc[i - m["rez"][v]]
        out[idx[i]] = val + m["phi"] ** j * m["u_final"]
    return pd.Series(expit(pd.Series(out)), name="remediado")


def backtest_remediado(d: pd.DataFrame, origenes: list[str], h: int = 12) -> pd.DataFrame:
    filas = []
    for o in origenes:
        rez = E.rezagos_elegidos(E.seleccionar_rezagos(d, fin=o))
        pr = pronostico_remediado(ajustar_remediado(d, rez, fin=o), d, h=h)
        for k, (mes, v) in enumerate(pr.items(), start=1):
            filas.append({"origen": o, "modelo": "remediado", "h": k, "mes": mes, "pred": v, "obs": d["icv90"].loc[mes]})
    b = pd.DataFrame(filas)
    b["error_pb"] = 1e4 * (b["pred"] - b["obs"])
    return b
