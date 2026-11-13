"""Caso de inversión: entrada de una plataforma digital al crédito de consumo en Colombia.

Separa con cuidado dos tipos de insumo:
  * Observados (SFC, BanRep): tamaño y crecimiento del mercado, cuota de entrantes digitales, tasas y
    tickets de desembolso, techo de usura, mora por producto y su sensibilidad al ciclo.
  * Supuestos de negocio (diccionario SUPUESTOS): CAC, costo operativo, LGD, fondeo, capital. Cada uno se
    somete a sensibilidad y a Monte Carlo; ninguno se presenta como dato.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "01-riesgo-estres-consumo"))
from comun import cartera, macro, tasas, usura  # noqa: E402

MONTO_MILES = 1_000  # yvb2-ppaa reporta montos desembolsados en miles de pesos
VENTANA = ("2021-07-01", "2022-06-30")  # último año completo publicado de tasas semanales
DIGITALES = {"Nu O Nu Financiera": "Nu", "Lulo Bank": "Lulo Bank", '"Rappipay"': "RappiPay"}

# Productos comparados: filtro en la base de tasas y producto equivalente en la base de cartera.
PRODUCTOS = {
    "Tarjeta de crédito": {"tasas": lambda t: t["tipo"].eq("TARJETAS DE CREDITO PERSONAS NATURALES") & ~t["subcuenta"].str.contains("AVANCE"),
                           "cartera": "Tarjeta de crédito", "usura": "CONSUMO Y ORDINARIO", "plazo_meses": 12},
    "Libre inversión": {"tasas": lambda t: t["modalidad"].eq("CREDITOS DE CONSUMO") & t["subcuenta"].isin(["ENTRE 366 Y 1095 DIAS", "ENTRE 1096 Y 1825"]),
                        "cartera": "Libre inversión", "usura": "CONSUMO Y ORDINARIO", "plazo_meses": 36},
    "Libranza": {"tasas": lambda t: t["modalidad"].eq("CREDITOS A TRAVES DE LIBRANZA"),
                 "cartera": "Libranza", "usura": "CONSUMO Y ORDINARIO", "plazo_meses": 60},
}


# ------------------------------------------------------------------ mercado
def mercado(c: pd.DataFrame | None = None) -> dict:
    c = cartera() if c is None else c
    co = c[c["familia"] == "Consumo"]
    ult, ini = co["mes"].max(), co["mes"].min()
    anios = (pd.Period(ult, "M") - pd.Period(ini, "M")).n / 12
    sp = co.groupby(["mes", "producto"])["saldo"].sum().unstack()
    tam = pd.DataFrame({"saldo_actual": sp.loc[ult], "saldo_inicial": sp.loc[ini]})
    tam["cagr"] = (tam["saldo_actual"] / tam["saldo_inicial"]) ** (1 / anios) - 1
    tam["participacion"] = tam["saldo_actual"] / tam["saldo_actual"].sum()
    dig = co[co["entidad"].isin(DIGITALES)].assign(marca=lambda x: x["entidad"].map(DIGITALES))
    dig_p = dig.groupby(["mes", "marca"])["saldo"].sum().unstack().fillna(0)
    cuota_tarjeta = (dig[dig["producto"] == "Tarjeta de crédito"].groupby("mes")["saldo"].sum()
                     / co[co["producto"] == "Tarjeta de crédito"].groupby("mes")["saldo"].sum()).dropna()
    tipo = co[co["mes"] == ult].groupby("tipo_entidad")["saldo"].sum()
    return {"tam": tam.sort_values("saldo_actual", ascending=False), "digitales": dig_p,
            "cuota_digital_tarjeta": cuota_tarjeta, "por_tipo": tipo / tipo.sum(), "ultimo": ult, "anios": anios}


# ------------------------------------------------------------------ precios
def usura_semanal(u: pd.DataFrame, modalidad: str, semanas: pd.Series) -> pd.Series:
    x = u[u["modalidad"] == modalidad].sort_values("desde")
    pos = np.searchsorted(x["desde"].values, semanas.values.astype("datetime64[ns]"), side="right") - 1
    val = x["usura"].values[np.clip(pos, 0, None)]
    return pd.Series(np.where(pos >= 0, val, np.nan), index=semanas.index)


def mediana_ponderada(v: np.ndarray, w: np.ndarray) -> float:
    orden = np.argsort(v)
    acum = np.cumsum(w[orden]) / w.sum()
    return float(v[orden][np.searchsorted(acum, 0.5)])


def precios(t: pd.DataFrame | None = None, u: pd.DataFrame | None = None) -> pd.DataFrame:
    """Tasa ponderada por monto, dispersión, margen frente al techo de usura y ticket, por producto,
    en la ventana del último año publicado."""
    t = tasas() if t is None else t
    u = usura() if u is None else u
    t = t[(t["semana"] >= VENTANA[0]) & (t["semana"] <= VENTANA[1])]
    filas = []
    for prod, cfg in PRODUCTOS.items():
        x = t[cfg["tasas"](t)].copy()
        x["usura"] = usura_semanal(u, cfg["usura"], x["semana"])
        x["margen_usura"] = x["usura"] - x["tasa_ea"]
        w = x["monto"]
        filas.append({
            "producto": prod, "registros": len(x),
            "tasa_ponderada": float((x["tasa_ea"] * w).sum() / w.sum()),
            "tasa_p10": float(x["tasa_ea"].quantile(0.10)), "tasa_p90": float(x["tasa_ea"].quantile(0.90)),
            "usura_promedio": float(x["usura"].mean()),
            "margen_usura_mediano_ponderado": mediana_ponderada(x["margen_usura"].to_numpy(), w.to_numpy()),
            "monto_a_menos_de_2pp_del_techo": float(w[x["margen_usura"] < 2].sum() / w.sum()),
            "ticket_millones": float(w.sum() * MONTO_MILES / x["n_creditos"].sum() / 1e6),
            "desembolsos_anuales_billones": float(w.sum() * MONTO_MILES / 1e12),
        })
    return pd.DataFrame(filas).set_index("producto")


def usura_vigente(u: pd.DataFrame | None = None, modalidad: str = "CONSUMO Y ORDINARIO") -> tuple[str, float]:
    u = usura() if u is None else u
    x = u[u["modalidad"] == modalidad].sort_values("desde").iloc[-1]
    return str(x["desde"].date()), float(x["usura"])


# ------------------------------------------------------------------ riesgo observado
def riesgo_producto(c: pd.DataFrame | None = None) -> pd.DataFrame:
    import estres as E  # proyecto 01
    c = cartera() if c is None else c
    p = E.por_producto(c)["icv90"].unstack()
    out = pd.DataFrame({"icv90_actual": p.iloc[-1], "icv90_promedio": p.mean(), "icv90_pico": p.max(),
                        "mes_pico": p.idxmax()})
    return out.loc[list(PRODUCTOS)]


# ------------------------------------------------------------------ economía unitaria
@dataclass
class Supuestos:
    """Supuestos de negocio de una plataforma digital. Todos se sensibilizan; ninguno es dato observado."""
    spread_fondeo_pp: float = 3.0          # sobre la TPM. +3: fondeo mayorista (CDT, líneas bancarias); -1: depósitos digitales
    opex_por_cliente: float = 120_000      # costo operativo anual por cliente activo (tecnología, servicio, cobranza)
    opex_pct_saldo: float = 0.01           # costo variable sobre saldo (procesamiento, seguros, GMF)
    cac: dict = field(default_factory=lambda: {"Tarjeta de crédito": 150_000, "Libre inversión": 250_000, "Libranza": 1_000_000})
    saldo_por_cliente: dict = field(default_factory=lambda: {"Tarjeta de crédito": 2.5e6, "Libre inversión": 9e6, "Libranza": 25e6})
    vida_cliente_anios: float = 3.0        # amortización del CAC
    lgd: dict = field(default_factory=lambda: {"Tarjeta de crédito": 0.75, "Libre inversión": 0.65, "Libranza": 0.40})
    multiplicador_perdida: float = 1.0     # 1,0 = ICV90 promedio del ciclo observado; >1 = estrés
    descuento_precio_pp: float = 2.0       # el entrante cobra por debajo del mercado para ganar cuota
    comisiones_tarjeta: float = 0.02       # intercambio sobre saldo promedio (facturación ~1,5 veces el saldo)
    capital_pct_saldo: float = 0.13        # solvencia mínima 9% + colchones y margen de gestión
    capital_minimo: float = 30e9           # supuesto de trabajo; verificar el monto vigente que publica la SFC
    impuesto: float = 0.35
    costo_capital: float = 0.18            # retorno exigido al patrimonio en COP


ESTRATEGIAS = {
    "Compañía de financiamiento, fondeo mayorista": {"spread_fondeo_pp": 3.0, "capital_minimo": 30e9},
    "Banco digital con depósitos": {"spread_fondeo_pp": -1.0, "opex_por_cliente": 150_000, "capital_minimo": 110e9},
}


def precio_entrante(pr: pd.DataFrame, prod: str, usura_hoy: float, s: Supuestos) -> float:
    """Precio = techo vigente - margen mediano observado frente al techo - descuento de entrada."""
    return usura_hoy - pr.loc[prod, "margen_usura_mediano_ponderado"] - s.descuento_precio_pp


def economia_unitaria(prod: str, pr: pd.DataFrame, rg: pd.DataFrame, tpm: float, usura_hoy: float,
                      s: Supuestos) -> dict:
    """Estado de resultados anual por peso de saldo promedio, en estado estable."""
    tasa = precio_entrante(pr, prod, usura_hoy, s) / 100
    rendimiento = np.log1p(tasa)  # tasa efectiva anual a continua, conservador para el ingreso devengado
    comisiones = s.comisiones_tarjeta if prod == "Tarjeta de crédito" else 0.0
    fondeo = np.log1p((tpm + s.spread_fondeo_pp) / 100)
    # Pérdida anual: el stock de mora 90+ aproxima un año de incumplimientos en consumo (castigo a 180-360 días).
    perdida = rg.loc[prod, "icv90_promedio"] * s.multiplicador_perdida * s.lgd[prod]
    cac = s.cac[prod] / s.saldo_por_cliente[prod] / s.vida_cliente_anios
    opex = s.opex_por_cliente / s.saldo_por_cliente[prod] + s.opex_pct_saldo
    capital = s.capital_pct_saldo
    # El capital propio no paga intereses: reduce el fondeo necesario.
    fondeo_neto = fondeo * (1 - capital)
    antes_imp = rendimiento + comisiones - fondeo_neto - perdida - opex - cac
    roa = antes_imp * (1 - s.impuesto)
    return {"producto": prod, "tasa_cliente": tasa, "rendimiento": rendimiento, "comisiones": comisiones,
            "fondeo": fondeo_neto, "perdida": perdida, "opex": opex, "cac": cac,
            "utilidad_antes_imp": antes_imp, "roa": roa, "roe": roa / capital,
            "spread_sobre_costo_capital": roa / capital - s.costo_capital}


# ------------------------------------------------------------------ plan a cinco años
def plan(prod: str, pr: pd.DataFrame, rg: pd.DataFrame, tpm: float, usura_hoy: float, s: Supuestos,
         clientes_meta: int = 400_000, meses: int = 60, opex_fijo_mensual: float = 2.5e9,
         multiplo_salida: float = 1.5) -> pd.DataFrame:
    """Plan mensual. Altas con curva logística hasta `clientes_meta` en el mes 36, deserción 2% mensual,
    saldo por cliente fijo, pérdida con maduración (la mora de una cosecha aparece entre los meses 6 y 18).
    El capital es el mayor entre el porcentaje regulatorio sobre saldo y un capital mínimo absoluto."""
    u = economia_unitaria(prod, pr, rg, tpm, usura_hoy, s)
    m = np.arange(1, meses + 1)
    objetivo = clientes_meta / (1 + np.exp(-(m - 18) / 4))
    clientes = np.zeros(meses)
    altas = np.zeros(meses)
    for i in range(meses):
        previo = clientes[i - 1] * 0.98 if i else 0
        altas[i] = max(objetivo[i] - previo, 0)
        clientes[i] = previo + altas[i]
    saldo = clientes * s.saldo_por_cliente[prod]
    # Maduración: la tasa de pérdida mensual de cada peso de saldo sube hasta su valor estable en 12 meses.
    madurez = np.minimum(np.arange(1, meses + 1) / 12, 1.0)
    edad_media = np.array([(madurez[:i + 1][::-1] * altas[:i + 1]).sum() / max(altas[:i + 1].sum(), 1) for i in range(meses)])
    ingreso = saldo * (u["rendimiento"] + u["comisiones"]) / 12
    fondeo = saldo * u["fondeo"] / 12
    perdida = saldo * u["perdida"] * edad_media / 12
    opex = saldo * s.opex_pct_saldo / 12 + clientes * s.opex_por_cliente / 12 + opex_fijo_mensual
    cac = altas * s.cac[prod]
    uai = ingreso - fondeo - perdida - opex - cac
    impuesto = np.where(uai > 0, uai * s.impuesto, 0)
    utilidad = uai - impuesto
    capital_req = np.maximum(saldo * s.capital_pct_saldo, s.capital_minimo)
    df = pd.DataFrame({"mes": m, "clientes": clientes, "altas": altas, "saldo": saldo, "ingreso": ingreso,
                       "fondeo": fondeo, "perdida": perdida, "opex": opex, "cac": cac, "utilidad": utilidad,
                       "capital_requerido": capital_req})
    # Aportes de capital: los necesarios para cubrir el requerimiento después de las pérdidas acumuladas.
    patrimonio, aportes = 0.0, []
    for i in range(meses):
        patrimonio += utilidad[i]
        falta = max(capital_req[i] - patrimonio, 0)
        aportes.append(falta)
        patrimonio += falta
    df["aporte"] = aportes
    df["patrimonio"] = np.cumsum(utilidad) + np.cumsum(aportes)
    df.attrs.update({"unitaria": u, "multiplo_salida": multiplo_salida})
    return df


def indicadores_plan(df: pd.DataFrame) -> dict:
    util_12 = df["utilidad"].rolling(12).sum()
    eq = df["patrimonio"].iloc[-1]
    flujos = -df["aporte"].to_numpy(copy=True)
    flujos[-1] += eq * df.attrs["multiplo_salida"]
    tir = _tir_mensual(flujos)
    positivo = df.index[df["utilidad"] > 0]
    return {"capital_aportado": float(df["aporte"].sum()), "saldo_final": float(df["saldo"].iloc[-1]),
            "mes_equilibrio": int(df.loc[positivo[0], "mes"]) if len(positivo) else None,
            "roe_anio5": float(util_12.iloc[-1] / df["patrimonio"].iloc[-13:-1].mean()),
            "tir_anual": (1 + tir) ** 12 - 1 if tir is not None else None}


def _tir_mensual(flujos: np.ndarray) -> float | None:
    lo, hi = -0.99, 1.0
    f = lambda r: np.sum(flujos / (1 + r) ** np.arange(len(flujos)))  # noqa: E731
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ incertidumbre
def combinar(planes: list[pd.DataFrame], capital_minimo: float, capital_pct: float, multiplo_salida: float = 1.5) -> pd.DataFrame:
    """Suma planes de producto que comparten licencia: los flujos se suman y el capital mínimo cuenta una vez."""
    cols = ["clientes", "altas", "saldo", "ingreso", "fondeo", "perdida", "opex", "cac", "utilidad"]
    df = sum(p[cols] for p in planes)
    df["mes"] = planes[0]["mes"]
    df["capital_requerido"] = np.maximum(df["saldo"] * capital_pct, capital_minimo)
    patrimonio, aportes = 0.0, []
    for i in range(len(df)):
        patrimonio += df["utilidad"].iloc[i]
        falta = max(df["capital_requerido"].iloc[i] - patrimonio, 0)
        aportes.append(falta)
        patrimonio += falta
    df["aporte"] = aportes
    df["patrimonio"] = np.cumsum(df["utilidad"]) + np.cumsum(aportes)
    df.attrs["multiplo_salida"] = multiplo_salida
    return df


def plan_cruzado(pr, rg, tpm, usura_hoy, s: Supuestos, clientes_tarjeta: int, tasa_cruce: float = 0.3,
                 cac_cruce: float = 50_000, mult_perdida_cruce: float = 0.8, inicio_cruce: int = 12) -> pd.DataFrame:
    """Tarjeta como producto de adquisición y libre inversión vendida a clientes con historial propio.
    El crédito cruzado tiene CAC bajo y menor pérdida esperada por selección con datos transaccionales
    (supuestos), y arranca cuando hay al menos `inicio_cruce` meses de comportamiento."""
    t = plan("Tarjeta de crédito", pr, rg, tpm, usura_hoy, s, clientes_meta=clientes_tarjeta)
    s2 = replace(s, cac={**s.cac, "Libre inversión": cac_cruce}, multiplicador_perdida=mult_perdida_cruce,
                 opex_por_cliente=s.opex_por_cliente * 0.4)  # servicio compartido con la tarjeta
    li = plan("Libre inversión", pr, rg, tpm, usura_hoy, s2, clientes_meta=int(clientes_tarjeta * tasa_cruce))
    li = li.copy()
    # Desplaza la curva de cruce: no hay crédito cruzado antes de `inicio_cruce`.
    for col in ["clientes", "altas", "saldo", "ingreso", "fondeo", "perdida", "opex", "cac", "utilidad", "capital_requerido"]:
        li[col] = np.r_[np.zeros(inicio_cruce), li[col].to_numpy()[:-inicio_cruce]]
    li["opex"] = li["opex"] - np.r_[np.zeros(inicio_cruce), np.full(len(li) - inicio_cruce, 2.5e9)]  # sin costo fijo adicional
    li["utilidad"] = (li["ingreso"] - li["fondeo"] - li["perdida"] - li["opex"] - li["cac"])
    li["utilidad"] = np.where(li["utilidad"] > 0, li["utilidad"] * (1 - s.impuesto), li["utilidad"])
    return combinar([t, li], s.capital_minimo, s.capital_pct_saldo)


def tornado(prod, pr, rg, tpm, usura_hoy, base: Supuestos) -> pd.DataFrame:
    rangos = {
        "spread_fondeo_pp": (base.spread_fondeo_pp - 1.5, base.spread_fondeo_pp + 2.0),
        "opex_por_cliente": (80_000, 220_000), "comisiones_tarjeta": (0.0, 0.03),
        "multiplicador_perdida": (0.7, 1.6), "capital_pct_saldo": (0.11, 0.16),
    }
    roe0 = economia_unitaria(prod, pr, rg, tpm, usura_hoy, base)["roe"]
    filas = []
    for k, (a, b) in rangos.items():
        r = [economia_unitaria(prod, pr, rg, tpm, usura_hoy, replace(base, **{k: v}))["roe"] for v in (a, b)]
        filas.append({"supuesto": k, "bajo": a, "alto": b, "roe_bajo": r[0], "roe_alto": r[1], "rango": abs(r[1] - r[0])})
    return pd.DataFrame(filas).sort_values("rango", ascending=False).assign(roe_base=roe0)


def montecarlo(prod, pr, rg, tpm, usura_hoy, base: Supuestos, n: int = 5000, semilla: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    filas = []
    for _ in range(n):
        s = replace(base,
                    spread_fondeo_pp=rng.triangular(base.spread_fondeo_pp - 1.5, base.spread_fondeo_pp, base.spread_fondeo_pp + 2.0),
                    opex_por_cliente=rng.triangular(80_000, base.opex_por_cliente, 220_000),
                    cac={k: v * rng.lognormal(0, 0.35) for k, v in base.cac.items()},
                    multiplicador_perdida=rng.lognormal(0, 0.25),
                    lgd={k: float(np.clip(v + rng.normal(0, 0.08), 0.2, 0.95)) for k, v in base.lgd.items()})
        u = economia_unitaria(prod, pr, rg, tpm, usura_hoy, s)
        filas.append({"roe": u["roe"], "spread": u["spread_sobre_costo_capital"], "perdida": u["perdida"],
                      "cac": s.cac[prod], "mult": s.multiplicador_perdida})
    return pd.DataFrame(filas)


def escala(prod, pr, rg, tpm, usura_hoy, s: Supuestos, metas=(200_000, 400_000, 800_000, 1_200_000, 2_000_000)) -> pd.DataFrame:
    """Con costos fijos y capital mínimo, la rentabilidad depende de la escala: ROE del año 5 y TIR por meta de clientes."""
    filas = []
    for m in metas:
        ind = indicadores_plan(plan(prod, pr, rg, tpm, usura_hoy, s, clientes_meta=m))
        filas.append({"clientes_meta": m, **ind})
    return pd.DataFrame(filas).set_index("clientes_meta")


def sensibilidad_tpm(prod, pr, rg, usura_hoy, s: Supuestos, tpms=(7.0, 9.0, 10.5, 12.25, 14.0)) -> pd.DataFrame:
    """El techo de usura se mueve con el interés bancario corriente, que sigue a las tasas de mercado con rezago;
    el fondeo se reprecia con la TPM más rápido. Se mantiene el techo vigente y se mueve la TPM: es el margen
    transitorio de un ciclo de recortes (o la compresión de uno de alzas)."""
    return pd.DataFrame([{"tpm": x, **economia_unitaria(prod, pr, rg, x, usura_hoy, s)} for x in tpms]).set_index("tpm")[["fondeo", "roa", "roe"]]
