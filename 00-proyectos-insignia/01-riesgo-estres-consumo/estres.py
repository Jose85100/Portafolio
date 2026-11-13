"""Estrés macro y apetito de riesgo para la cartera de consumo del sistema financiero colombiano.

Todas las cifras salen de la capa de datos compartida (SFC, BanRep, DANE). Las funciones son puras
sobre DataFrames para que la validación independiente (proyecto 02) pueda reutilizarlas o reemplazarlas.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun import cartera, expit, logit, macro  # noqa: E402

PRODUCTOS = ["Libranza", "Libre inversión", "Tarjeta de crédito", "Vehículo", "Rotativo"]
# LGD supuestas por producto (garantía y fuente de pago). Son supuestos de trabajo, no estimaciones.
LGD = {"Libranza": 0.40, "Libre inversión": 0.65, "Tarjeta de crédito": 0.75, "Vehículo": 0.40,
       "Rotativo": 0.70, "Otros consumo": 0.70, "Consumo bajo monto": 0.80, "Consumo empleados": 0.30}
COVID = ("2020-04", "2021-03")  # periodo de alivios (Circulares Externas 007 y 014 de 2020 de la SFC)
MAX_REZAGO = 24


# ---------------------------------------------------------------- series
def series_consumo(c: pd.DataFrame | None = None) -> pd.DataFrame:
    """Serie mensual del sistema para consumo: saldo, mora, ICV90, mora temprana y crecimiento anual."""
    c = cartera() if c is None else c
    s = c[c["familia"] == "Consumo"].groupby("mes")[["saldo", "mora30", "mora90", "mora_1_2m"]].sum()
    s["icv90"] = s["mora90"] / s["saldo"]
    s["icv30"] = s["mora30"] / s["saldo"]
    s["temprana"] = s["mora_1_2m"] / s["saldo"]
    s["crec"] = 100 * s["saldo"].pct_change(12)
    return s


def por_producto(c: pd.DataFrame | None = None, campo: str = "producto") -> pd.DataFrame:
    c = cartera() if c is None else c
    p = c[c["familia"] == "Consumo"].groupby(["mes", campo])[["saldo", "mora90"]].sum()
    p["icv90"] = p["mora90"] / p["saldo"]
    return p


def base_modelo(s: pd.DataFrame | None = None, m: pd.DataFrame | None = None) -> pd.DataFrame:
    s = series_consumo() if s is None else s
    m = macro() if m is None else m
    d = s.join(m, how="left")
    d["y"] = logit(d["icv90"])
    per = pd.PeriodIndex(d.index, freq="M")
    d["covid"] = ((per >= pd.Period(COVID[0], "M")) & (per <= pd.Period(COVID[1], "M"))).astype(int)
    return d


# ---------------------------------------------------------------- 1. descomposición
def shift_share(p: pd.DataFrame, t0: str, t1: str) -> pd.DataFrame:
    """Descompone el cambio del ICV90 agregado entre t0 y t1 en efecto tasa (dentro de producto),
    efecto mezcla (cambio de participación) e interacción. Suma exactamente el cambio total."""
    a, b = p.xs(t0), p.xs(t1)
    w0, w1 = a["saldo"] / a["saldo"].sum(), b["saldo"] / b["saldo"].sum()
    r0, r1 = a["icv90"], b["icv90"]
    idx = r0.index.intersection(r1.index)
    w0, w1, r0, r1 = w0[idx], w1[idx], r0[idx], r1[idx]
    out = pd.DataFrame({
        "peso_inicial": w0, "peso_final": w1, "icv90_inicial": r0, "icv90_final": r1,
        "efecto_tasa": w0 * (r1 - r0), "efecto_mezcla": (w1 - w0) * r0, "interaccion": (w1 - w0) * (r1 - r0),
    })
    out["total"] = out[["efecto_tasa", "efecto_mezcla", "interaccion"]].sum(axis=1)
    return out.sort_values("total", ascending=False)


# ---------------------------------------------------------------- 2. alerta temprana
def correlaciones_adelanto(d: pd.DataFrame, rezagos=(0, 3, 6, 9, 12, 18, 24)) -> pd.DataFrame:
    filas = []
    for L in rezagos:
        filas.append({"rezago_meses": L, **{v: d["icv90"].corr(d[v].shift(L))
                                            for v in ["temprana", "desempleo_12m", "tpm", "inflacion", "crec"]}})
    return pd.DataFrame(filas).set_index("rezago_meses")


def panel_alerta_temprana(c: pd.DataFrame | None = None, saldo_min: float = 1e11, h: int = 3) -> dict:
    """¿El aumento de la mora temprana (31-60 días) de una entidad anticipa su mora 90+?
    Regresión panel: cambio de ICV90 en t..t+h sobre cambio de mora temprana en t-h..t, con efectos
    fijos de mes (absorbe el ciclo común) y errores agrupados por entidad."""
    c = cartera() if c is None else c
    e = c[c["familia"] == "Consumo"].groupby(["codigo_entidad", "mes"])[["saldo", "mora90", "mora_1_2m"]].sum()
    e = e[e["saldo"] > saldo_min].copy()
    e["r90"] = e["mora90"] / e["saldo"]
    e["tem"] = e["mora_1_2m"] / e["saldo"]
    g = e.groupby(level=0)
    e["y"] = 100 * (g["r90"].shift(-h) - e["r90"])
    e["x"] = 100 * g["tem"].diff(h)
    E = e.dropna(subset=["y", "x"]).reset_index()
    # Recorte de extremos (fusiones, castigos masivos) al 1% por cola.
    lo, hi = E[["x", "y"]].quantile(0.01), E[["x", "y"]].quantile(0.99)
    E = E[(E["x"].between(lo.x, hi.x)) & (E["y"].between(lo.y, hi.y))]
    E["x_dm"] = E["x"] - E.groupby("mes")["x"].transform("mean")
    E["y_dm"] = E["y"] - E.groupby("mes")["y"].transform("mean")
    r = sm.OLS(E["y_dm"], E[["x_dm"]]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(E["codigo_entidad"])[0]})
    return {"beta": float(r.params["x_dm"]), "t": float(r.tvalues["x_dm"]), "n": int(len(E)),
            "entidades": int(E["codigo_entidad"].nunique()), "datos": E}


# ---------------------------------------------------------------- 3. modelo satélite
@dataclass
class Satelite:
    rezagos: dict
    resultado: object
    muestra: pd.Index

    @property
    def params(self) -> pd.Series:
        return self.resultado.params

    def multiplicadores_largo_plazo(self) -> pd.Series:
        rho = self.params["ylag"]
        return self.params[["tpm", "inflacion", "crec"]] / (1 - rho)


def matriz(d: pd.DataFrame, rez: dict) -> pd.DataFrame:
    return pd.DataFrame({
        "y": d["y"], "ylag": d["y"].shift(1),
        "tpm": d["tpm"].shift(rez["tpm"]), "inflacion": d["inflacion"].shift(rez["inflacion"]),
        "crec": d["crec"].shift(rez["crec"]), "covid": d["covid"],
    }, index=d.index)


def seleccionar_rezagos(d: pd.DataFrame, fin: str | None = None) -> pd.DataFrame:
    """Rejilla de rezagos comparada por AIC sobre una muestra común (el inicio lo fija el rezago máximo,
    para que todos los modelos se estimen con las mismas observaciones). Marca si los tres coeficientes
    macro tienen el signo económico esperado (positivo): más tasa, más inflación y más crecimiento pasado
    del crédito deben subir la mora. La selección final solo considera especificaciones coherentes."""
    d = d if fin is None else d.loc[:fin]
    inicio = d.index[MAX_REZAGO + 12]  # +12 porque crec ya consume 12 meses
    filas = []
    for lt in (3, 6, 9, 12):
        for li in (6, 9, 12, 15, 18):
            for lc in (12, 15, 18, 21, 24):
                rez = {"tpm": lt, "inflacion": li, "crec": lc}
                Z = matriz(d, rez).loc[inicio:].dropna()
                r = sm.OLS(Z["y"], sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
                filas.append({**rez, "aic": r.aic, "n": len(Z),
                              **{f"b_{k}": r.params[k] for k in ("tpm", "inflacion", "crec")},
                              **{f"p_{k}": r.pvalues[k] for k in ("tpm", "inflacion", "crec")}})
    t = pd.DataFrame(filas).sort_values("aic").reset_index(drop=True)
    assert t["n"].nunique() == 1, "las comparaciones AIC deben usar la misma muestra"
    t["signos_ok"] = (t[["b_tpm", "b_inflacion", "b_crec"]] > 0).all(axis=1)
    return t


def rezagos_elegidos(tabla: pd.DataFrame) -> dict:
    fila = tabla[tabla["signos_ok"]].iloc[0]
    return {k: int(fila[k]) for k in ("tpm", "inflacion", "crec")}


def ajustar(d: pd.DataFrame, rez: dict, fin: str | None = None) -> Satelite:
    dd = d if fin is None else d.loc[:fin]
    Z = matriz(dd, rez).dropna()
    r = sm.OLS(Z["y"], sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    return Satelite(rez, r, Z.index)


# ---------------------------------------------------------------- 4. escenarios
def trayectorias_macro(d: pd.DataFrame, horizonte: int = 24) -> dict[str, pd.DataFrame]:
    """Escenarios desde el último mes con cartera observada. Choques en rampa de 6 meses y luego planos.
    Severidad anclada en la historia de la muestra: en el ciclo 2021-2023 la TPM subió 11,5 pp y la
    inflación 11,7 pp; el severo equivale a cerca de la mitad de ese ciclo y el adverso a un cuarto."""
    ultimo = d["icv90"].last_valid_index()
    futuro = pd.period_range(pd.Period(ultimo, "M") + 1, periods=horizonte, freq="M").astype(str)
    base = {v: float(d.loc[ultimo, v]) for v in ["tpm", "inflacion"]}
    rampa = np.minimum(np.arange(1, horizonte + 1) / 6, 1.0)
    choques = {"Base": (0.0, 0.0), "Adverso": (3.0, 4.0), "Severo": (6.0, 8.0)}
    out = {}
    for nombre, (dtpm, dinf) in choques.items():
        f = pd.DataFrame(index=futuro)
        f["tpm"] = base["tpm"] + dtpm * rampa
        f["inflacion"] = base["inflacion"] + dinf * rampa
        # El crédito se desacelera bajo estrés: -0, -5, -10 pp sobre el último crecimiento.
        f["crec"] = float(d.loc[ultimo, "crec"]) - {"Base": 0, "Adverso": 5, "Severo": 10}[nombre] * rampa
        f["covid"] = 0
        out[nombre] = f
    return out


def proyectar(sat: Satelite, d: pd.DataFrame, futuro: pd.DataFrame) -> pd.Series:
    """Proyección recursiva del logit del ICV90. Los regresores rezagados usan historia observada mientras
    exista y la trayectoria del escenario después."""
    hist = d[["tpm", "inflacion", "crec", "covid", "y"]].copy()
    ultimo = d["icv90"].last_valid_index()
    hist = hist.loc[:ultimo]
    todo = pd.concat([hist, futuro.assign(y=np.nan)])
    p = sat.params
    for mes in futuro.index:
        i = todo.index.get_loc(mes)
        x = {"const": 1.0, "ylag": todo["y"].iloc[i - 1], "covid": 0.0}
        for v in ["tpm", "inflacion", "crec"]:
            x[v] = todo[v].iloc[i - sat.rezagos[v]]
        todo.iloc[i, todo.columns.get_loc("y")] = sum(p[k] * x[k] for k in p.index)
    return pd.Series(expit(todo.loc[futuro.index, "y"]), index=futuro.index, name="icv90")


def sensibilidades_producto(p: pd.DataFrame, s: pd.DataFrame) -> pd.DataFrame:
    """Beta de cada producto frente al sistema en escala logit: logit(icv_p) = a + b logit(icv_sistema)."""
    filas = []
    for prod in PRODUCTOS:
        y = logit(p.xs(prod, level="producto")["icv90"])
        x = logit(s["icv90"].reindex(y.index))
        r = sm.OLS(y, sm.add_constant(x)).fit()
        filas.append({"producto": prod, "a": r.params.iloc[0], "b": r.params.iloc[1], "r2": r.rsquared})
    return pd.DataFrame(filas).set_index("producto")


def impacto_perdida(proy: dict[str, pd.Series], s: pd.DataFrame, p: pd.DataFrame, betas: pd.DataFrame) -> pd.DataFrame:
    """Pérdida incremental aproximada: (ICV90 pico del escenario - ICV90 actual) x saldo actual x LGD,
    por producto. Es un orden de magnitud para el comité, no una medición de provisiones NIIF 9."""
    ultimo = s["icv90"].last_valid_index()
    actual = p.xs(ultimo, level="mes")
    filas = []
    for esc, serie in proy.items():
        pico_sis = serie.max()
        for prod, b in betas.iterrows():
            icv_act = actual.loc[prod, "icv90"]
            # Se proyecta el cambio en logit del sistema sobre el logit actual del producto.
            pico = float(expit(logit(icv_act) + b["b"] * (logit(pico_sis) - logit(s.loc[ultimo, "icv90"]))))
            saldo = actual.loc[prod, "saldo"]
            filas.append({"escenario": esc, "producto": prod, "icv90_actual": icv_act, "icv90_pico": pico,
                          "saldo": saldo, "lgd": LGD[prod], "perdida_incremental": max(pico - icv_act, 0) * saldo * LGD[prod]})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- 5. apetito de riesgo
def marco_apetito(p: pd.DataFrame, impacto: pd.DataFrame) -> pd.DataFrame:
    """Umbrales por producto: apetito = percentil 75 histórico, tolerancia = percentil 90,
    capacidad = pico del escenario severo. Estado del último mes contra esos umbrales."""
    ultimo = p.index.get_level_values("mes").max()
    filas = []
    for prod in PRODUCTOS:
        h = p.xs(prod, level="producto")["icv90"]
        sev = impacto.query("escenario == 'Severo' and producto == @prod")["icv90_pico"].iloc[0]
        ap, tol = h.quantile(0.75), h.quantile(0.90)
        act = h.loc[ultimo]
        estado = "Verde" if act <= ap else ("Ámbar" if act <= tol else "Rojo")
        filas.append({"producto": prod, "actual": act, "apetito_p75": ap, "tolerancia_p90": tol,
                      "capacidad_severo": max(sev, tol), "estado": estado})
    return pd.DataFrame(filas).set_index("producto")


def semaforo_entidades(c: pd.DataFrame | None = None, saldo_min: float = 5e11) -> pd.DataFrame:
    """Entidades con cartera de consumo relevante: ICV90 actual frente a la mediana del sistema y su
    tendencia de 6 meses en mora temprana. Es una lista de seguimiento, no un juicio sobre la entidad."""
    c = cartera() if c is None else c
    co = c[c["familia"] == "Consumo"]
    tipo = co.drop_duplicates("entidad", keep="last").set_index("entidad")["tipo_entidad"]
    e = co.groupby(["entidad", "mes"])[["saldo", "mora90", "mora_1_2m"]].sum()
    e["icv90"] = e["mora90"] / e["saldo"]
    e["temprana"] = e["mora_1_2m"] / e["saldo"]
    ult = e.index.get_level_values("mes").max()
    hace6 = str(pd.Period(ult, "M") - 6)
    a = e.xs(ult, level="mes")
    b = e.xs(hace6, level="mes").reindex(a.index)
    t = a[a["saldo"] > saldo_min].copy()
    t["tipo_entidad"] = tipo.reindex(t.index)
    t["delta_temprana_6m_pb"] = 1e4 * (t["temprana"] - b.loc[t.index, "temprana"])
    med = (t["mora90"].sum() / t["saldo"].sum())
    t["vs_sistema"] = t["icv90"] / med
    t["senal"] = np.select([(t["vs_sistema"] > 1.5) & (t["delta_temprana_6m_pb"] > 0),
                            (t["vs_sistema"] > 1.5) | (t["delta_temprana_6m_pb"] > 25)],
                           ["Seguimiento reforzado", "Vigilar"], "Normal")
    t = t.sort_values("saldo", ascending=False)
    # Se publican con código anónimo: es una señal estadística sobre datos agregados públicos y no
    # sustituye la información de supervisión ni la de la propia entidad.
    t.insert(0, "codigo", [f"E{i:02d}" for i in range(1, len(t) + 1)])
    return t.reset_index(drop=True)
