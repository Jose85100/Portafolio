"""Benchmark de mercado de tarjeta de crédito en Colombia con datos abiertos.

Fuentes: conjuntos de la Superintendencia Financiera de Colombia (SFC)
publicados en datos.gov.co (API Socrata, sin clave). Todo es información
agregada por entidad y mes; no contiene datos de personas.

Flujo:
    1. ``descargar(destino)`` consulta la API y deja CSV compactos en
       ``datos_publicos/``. Solo se ejecuta a mano (``python mercado_publico.py``);
       los notebooks leen la copia guardada para no depender de la red.
    2. ``cargar(destino)`` lee esa copia.
    3. ``indicadores_entidad`` y ``indicadores_mercado`` calculan las métricas
       del benchmark con definiciones explícitas.

Las funciones de transformación son puras y tienen pruebas en
``tests/test_mercado_publico.py``.
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

BASE_API = "https://www.datos.gov.co/resource/{id}.csv"

FUENTES = pd.DataFrame(
    [
        ("h2jg-r3zg", "Tarjetas de crédito y débito", "SFC",
         "entidad × franquicia × mes", "2015-01",
         "tarjetas vigentes, canceladas y bloqueadas por tipo de persona; número y monto de compras y avances; "
         "intereses corrientes y de mora; castigos; saldo; cupo no utilizado; tarifas de intercambio"),
        ("rvii-eis8", "Distribución de cartera por producto", "SFC",
         "entidad × producto × mes", "2015-01",
         "saldo por altura de mora (30-60, 60-90, 90-180, >180 días), clientes en mora y calificación A-E; "
         "tarjeta separada por ingreso hasta 2 SMMLV y superior"),
        ("w9zh-vetq", "Tasas de interés activas por tipo de crédito (histórico)", "SFC",
         "entidad × semana × producto × persona × municipio × clase de deudor", "2022-01",
         "tasa efectiva promedio, monto y número desembolsado; el API falla con consultas grandes"),
        ("pare-7x5i", "Tasa de interés bancario corriente (TIBC)", "SFC",
         "resolución × modalidad", "2014-12",
         "tasa certificada; la usura es 1,5 veces la TIBC de consumo y ordinario"),
    ],
    columns=["id", "nombre", "publica", "granularidad", "desde", "contenido"],
)

# Franquicias de crédito en h2jg (6 = débito y 7 = sistemas de pago de bajo valor se excluyen).
FRANQUICIAS_CREDITO = ("1", "2", "3", "4", "5")

# Descripción oficial (normalizada) -> nombre corto. Las subcuentas cambian de
# número entre formatos, por eso se mapea por texto y no por código.
METRICAS_TARJETA = {
    "numero total de tarjetas de credito vigentes a la fecha de corte": "tarjetas_vigentes",
    "numero total de tarjetas de credito vigentes durante el mes": "tarjetas_vigentes_mes",
    "numero total de tarjetas de credito canceladas": "tarjetas_canceladas",
    "numero total de tarjetas de creditos bloqueadas temporalmente": "tarjetas_bloqueadas",
    "numero de transacciones por compras a nivel nacional con tarjeta de credito": "n_compras",
    "numero de transacciones por avances a nivel nacional con tarjeta de credito": "n_avances",
    "numero de transacciones por compras en el exterior con tarjeta de credito": "n_compras_exterior",
    "monto de las transacciones por compras con tarjeta de credito a nivel nacional": "monto_compras",
    "monto de las transacciones por avances con tarjeta de credito a nivel nacional": "monto_avances",
    "monto de las transacciones por compras en el exterior con tarjeta de credito": "monto_compras_exterior",
    "monto de los intereses corrientes por compras y avances con tarjeta de credito": "intereses_corrientes",
    "monto de los intereses de mora por compras y avances con tarjeta de credito": "intereses_mora",
    "monto de los castigos de cartera por tarjeta de credito, unicamente capital.": "castigos_capital",
    "monto de los castigos de cartera por tarjeta de credito, conceptos diferentes a capital": "castigos_otros",
    "saldo de la cartera por tarjeta de credito": "saldo_tarjeta",
    "total cupo de credito no utilizado por todos los tarjetahabientes": "cupo_no_utilizado",
}

TIPOS_ENTIDAD = {1: "Banco", 4: "Compañía de financiamiento", 32: "Cooperativa financiera"}

# Columnas de rvii-eis8 que usa la tarjeta (las demás alturas aplican a otras modalidades).
COLUMNAS_MORA = {
    "_1_saldo_de_la_cartera_a": "saldo",
    "_2_vigente": "vigente",
    "_3_vencida_1_2_meses": "mora_30_60",
    "_4_vencida_2_3_meses": "mora_60_90",
    "_8_vencida_3_6_meses": "mora_90_180",
    "_9_vencida_6_meses": "mora_180_mas",
    "_16_n_mero_de_clientes_mora": "clientes_mora",
    "_18_calificaci_n_de_riesgo": "saldo_A",
    "_20_calificaci_n_de_riesgo": "saldo_B",
    "_22_calificaci_n_de_riesgo": "saldo_C",
    "_24_calificaci_n_de_riesgo": "saldo_D",
    "_26_calificaci_n_de_riesgo": "saldo_E",
}
SEGMENTO_INGRESO = {5: "total", 10: "ingreso_hasta_2_smmlv", 15: "ingreso_superior_2_smmlv"}

PRODUCTOS_TASAS = (
    "Tarjeta de crédito para ingresos hasta 2 SMMLV",
    "Tarjeta de crédito para ingresos superiores a 2 SMMLV",
    "Tarjeta de crédito empresarial",
)


# --------------------------------------------------------------------------- descarga
def _normalizar(texto: str) -> str:
    import unicodedata

    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(t.lower().split())


def socrata(dataset: str, params: dict, intentos: int = 5, timeout: int = 240) -> pd.DataFrame:
    """Consulta un conjunto de datos.gov.co y devuelve un DataFrame (formato CSV)."""
    import requests

    ultimo = None
    for i in range(intentos):
        try:
            r = requests.get(BASE_API.format(id=dataset), params=params, timeout=timeout)
            r.raise_for_status()
            return pd.read_csv(io.StringIO(r.text), low_memory=False)
        except Exception as exc:  # la API de la SFC falla de forma intermitente
            ultimo = exc
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"{dataset}: la consulta falló {intentos} veces ({ultimo})")


def _paginar(dataset: str, where: str, lote: int = 50_000) -> pd.DataFrame:
    partes, offset = [], 0
    while True:
        df = socrata(dataset, {"$where": where, "$limit": lote, "$offset": offset, "$order": ":id"})
        partes.append(df)
        if len(df) < lote:
            return pd.concat(partes, ignore_index=True)
        offset += lote


def _trimestres(desde: str, hasta: str):
    inicio = pd.Period(desde, "Q")
    fin = pd.Period(hasta, "Q")
    for q in pd.period_range(inicio, fin, freq="Q"):
        yield q.start_time.date().isoformat(), q.end_time.date().isoformat()


def descargar(destino: Path, desde_tasas: str = "2022-01-01", verbose: bool = True) -> dict:
    """Descarga y deja en ``destino`` los CSV compactos del benchmark."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    log = (lambda *a: print(*a, flush=True)) if verbose else (lambda *a: None)
    franq = ",".join(f"'{f}'" for f in FRANQUICIAS_CREDITO)

    log("tarjetas (h2jg-r3zg)…")
    tarjetas = tidy_tarjetas(_paginar("h2jg-r3zg", f"cod_uca in ({franq})"))
    tarjetas.to_csv(destino / "sfc_tarjetas_entidad_mes.csv.gz", index=False)

    log("cartera por altura de mora (rvii-eis8)…")
    cartera = tidy_cartera(_paginar("rvii-eis8", "unicap in ('1','2','3','4','5','6')"))
    cartera.to_csv(destino / "sfc_cartera_consumo_mora.csv.gz", index=False)

    log("TIBC (pare-7x5i)…")
    tidy_tibc(socrata("pare-7x5i", {"$limit": 5000})).to_csv(destino / "sfc_tibc.csv.gz", index=False)

    log("desembolsos y tasas de tarjeta (w9zh-vetq), por trimestre…")
    productos = ",".join(f"'{p}'" for p in PRODUCTOS_TASAS)
    partes = []
    hoy = pd.Timestamp.today().normalize().date().isoformat()
    for ini, fin in _trimestres(desde_tasas, hoy):
        q = (
            "SELECT fecha_corte, tipo_entidad, codigo_entidad, nombre_entidad, producto_de_cr_dito, "
            "tipo_de_persona, clase_deudor, sum(montos_desembolsados) AS monto, "
            "sum(numero_de_creditos) AS n, sum(tasa_efectiva_promedio * montos_desembolsados) AS tasa_x_monto "
            f"WHERE producto_de_cr_dito in ({productos}) AND fecha_corte between '{ini}' and '{fin}T23:59:59' "
            "GROUP BY fecha_corte, tipo_entidad, codigo_entidad, nombre_entidad, producto_de_cr_dito, "
            "tipo_de_persona, clase_deudor LIMIT 50000"
        )
        try:
            partes.append(socrata("w9zh-vetq", {"$query": q}))
            log(f"  {ini} ok ({len(partes[-1])} filas)")
        except RuntimeError as exc:
            log(f"  {ini} sin datos: {exc}")
    desembolsos = tidy_desembolsos(pd.concat([p for p in partes if len(p)], ignore_index=True))
    desembolsos.to_csv(destino / "sfc_desembolsos_tarjeta.csv.gz", index=False)

    # Último trimestre con datos completos: el API publica con rezago de varias semanas.
    ultima = pd.Timestamp(desembolsos["semana"].max())
    hoy_q = pd.Period(ultima, "Q") - (0 if ultima >= pd.Period(ultima, "Q").end_time - pd.Timedelta(days=7) else 1)
    geo = descargar_geo(hoy_q, log)
    geo.to_csv(destino / "sfc_desembolsos_tarjeta_departamento.csv.gz", index=False)
    return escribir_metadatos(destino, tarjetas, cartera, desembolsos, str(hoy_q))


def descargar_geo(trimestre: pd.Period, log=print) -> pd.DataFrame:
    """Desembolsos de tarjeta por municipio, mes a mes (el trimestre completo agota el tiempo del API)."""
    productos = ",".join(f"'{p}'" for p in PRODUCTOS_TASAS)
    partes = []
    for mes in pd.period_range(trimestre.start_time, trimestre.end_time, freq="M"):
        ini, fin = mes.start_time.date().isoformat(), mes.end_time.date().isoformat()
        q = (
            "SELECT codigo_municipio, producto_de_cr_dito, clase_deudor, sum(montos_desembolsados) AS monto, "
            "sum(numero_de_creditos) AS n, sum(tasa_efectiva_promedio * montos_desembolsados) AS tasa_x_monto "
            f"WHERE producto_de_cr_dito in ({productos}) AND fecha_corte between '{ini}' and '{fin}T23:59:59' "
            "GROUP BY codigo_municipio, producto_de_cr_dito, clase_deudor LIMIT 50000"
        )
        partes.append(socrata("w9zh-vetq", {"$query": q}))
        log(f"  {mes} ok ({len(partes[-1])} filas)")
    raw = pd.concat(partes, ignore_index=True)
    return tidy_geo(raw, periodo=str(trimestre))


def escribir_metadatos(destino: Path, tarjetas, cartera, desembolsos, trimestre_geo: str) -> dict:
    meta = {
        "descargado": pd.Timestamp.now(tz="America/Bogota").isoformat(timespec="seconds"),
        "fuentes": FUENTES[["id", "nombre"]].to_dict("records"),
        "corte_tarjetas": str(pd.to_datetime(tarjetas["fecha"]).max())[:10],
        "corte_cartera": str(pd.to_datetime(cartera["fecha"]).max())[:10],
        "corte_desembolsos": str(pd.to_datetime(desembolsos["semana"]).max())[:10],
        "trimestre_geo": trimestre_geo,
    }
    (Path(destino) / "metadatos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


# --------------------------------------------------------------------------- limpieza
def tidy_tarjetas(raw: pd.DataFrame) -> pd.DataFrame:
    """h2jg-r3zg -> una fila por entidad × mes; columnas = métricas sumadas en franquicias.

    Las cantidades de tarjetas vienen separadas por persona natural y jurídica;
    se guardan como ``<metrica>_natural`` y ``<metrica>_juridica``.
    """
    df = raw.copy()
    df = df[df["cod_uca"].astype(str).isin(FRANQUICIAS_CREDITO)]
    df["metrica"] = df["descripcion"].map(lambda s: METRICAS_TARJETA.get(_normalizar(s)))
    df = df[df["metrica"].notna()]
    for c in ("persona_natural", "persona_juridica", "total_tarjetas"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["fecha"] = pd.to_datetime(df["fechacorte"]).dt.to_period("M").dt.to_timestamp("M")
    keys = ["tipoentidad", "codigoentidad", "fecha"]
    tot = df.pivot_table(index=keys, columns="metrica", values="total_tarjetas", aggfunc="sum")
    conteos = [m for m in ("tarjetas_vigentes", "tarjetas_canceladas") if m in tot.columns]
    nat = df[df["metrica"].isin(conteos)].pivot_table(index=keys, columns="metrica", values="persona_natural", aggfunc="sum")
    jur = df[df["metrica"].isin(conteos)].pivot_table(index=keys, columns="metrica", values="persona_juridica", aggfunc="sum")
    out = tot.join(nat.add_suffix("_natural")).join(jur.add_suffix("_juridica")).reset_index()
    out.columns.name = None
    nombres = (df.sort_values("fecha").groupby(["tipoentidad", "codigoentidad"])["nombreentidad"].last()
               .rename("entidad").reset_index())
    out = out.merge(nombres, on=["tipoentidad", "codigoentidad"], how="left")
    out = out.rename(columns={"tipoentidad": "tipo_entidad", "codigoentidad": "codigo_entidad"})
    out["entidad"] = out["entidad"].map(nombre_corto)
    return etiquetar(out).sort_values(["fecha", "tipo_entidad", "codigo_entidad"]).reset_index(drop=True)


def tidy_cartera(raw: pd.DataFrame) -> pd.DataFrame:
    """rvii-eis8 -> entidad × mes × producto × segmento con saldos por altura de mora."""
    df = raw.copy()
    df["unicap"] = df["unicap"].astype(int)
    df["renglon"] = df["renglon"].astype(int)
    # Se conserva el total de cada producto; para tarjeta, también los dos segmentos de ingreso.
    df = df[(df["renglon"] == 5) | ((df["unicap"] == 2) & df["renglon"].isin([10, 15]))]
    df["producto"] = df["descrip_uc"].map(_normalizar).str.upper()
    df["segmento"] = np.where(df["unicap"] == 2, df["renglon"].map(SEGMENTO_INGRESO), "total")
    df["fecha"] = pd.to_datetime(df["fecha_corte"]).dt.to_period("M").dt.to_timestamp("M")
    cols = {k: v for k, v in COLUMNAS_MORA.items() if k in df.columns}
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    g = (df.groupby(["tipo_entidad", "codigo_entidad", "fecha", "producto", "segmento"], as_index=False)[list(cols)]
         .sum().rename(columns=cols))
    nombres = (df.sort_values("fecha").groupby(["tipo_entidad", "codigo_entidad"])["nombreentidad"].last()
               .map(nombre_corto).rename("entidad").reset_index())
    return etiquetar(g.merge(nombres, on=["tipo_entidad", "codigo_entidad"], how="left"))


def tidy_tibc(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["tibc_ea"] = pd.to_numeric(df["interes_bancario_corriente"].astype(str).str.replace("%", "").str.replace(",", "."),
                                  errors="coerce") / 100
    df["desde"] = pd.to_datetime(df["vigencia_desde"])
    df["hasta"] = pd.to_datetime(df["vigencia_hasta"])
    df["modalidad"] = df["modalidad"].str.strip().str.upper()
    df["usura_ea"] = 1.5 * df["tibc_ea"]
    return df[["modalidad", "desde", "hasta", "tibc_ea", "usura_ea", "resolucion"]].sort_values(["modalidad", "desde"])


def usura_mensual(tibc: pd.DataFrame, modalidad: str = "CONSUMO Y ORDINARIO") -> pd.Series:
    """Tasa de usura vigente al cierre de cada mes para una modalidad."""
    t = tibc[tibc["modalidad"].str.contains(modalidad.split()[0]) & tibc["modalidad"].str.contains("ORDINARIO")]
    meses = pd.date_range(t["desde"].min(), t["hasta"].max(), freq="ME")
    vals = []
    for m in meses:
        fila = t[(t["desde"] <= m) & (t["hasta"] >= m)]
        vals.append(fila["usura_ea"].iloc[-1] if len(fila) else np.nan)
    return pd.Series(vals, index=meses, name="usura_ea")


def tidy_desembolsos(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    for c in ("monto", "n", "tasa_x_monto"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["semana"] = pd.to_datetime(df["fecha_corte"])
    df["producto"] = df["producto_de_cr_dito"].map({
        PRODUCTOS_TASAS[0]: "ingreso_hasta_2_smmlv",
        PRODUCTOS_TASAS[1]: "ingreso_superior_2_smmlv",
        PRODUCTOS_TASAS[2]: "empresarial",
    })
    df["deudor_nuevo"] = df["clase_deudor"].astype(str).str.contains("nuevo", case=False)
    df["entidad"] = df["nombre_entidad"].map(nombre_corto)
    df = etiquetar(df)
    keep = ["semana", "tipo_entidad", "codigo_entidad", "entidad", "producto", "tipo_de_persona",
            "deudor_nuevo", "monto", "n", "tasa_x_monto"]
    return (df[keep].groupby(keep[:-3], as_index=False)[["monto", "n", "tasa_x_monto"]].sum()
            .sort_values("semana").reset_index(drop=True))


DEPARTAMENTOS = {
    5: "Antioquia", 8: "Atlántico", 11: "Bogotá D.C.", 13: "Bolívar", 15: "Boyacá", 17: "Caldas",
    18: "Caquetá", 19: "Cauca", 20: "Cesar", 23: "Córdoba", 25: "Cundinamarca", 27: "Chocó",
    41: "Huila", 44: "La Guajira", 47: "Magdalena", 50: "Meta", 52: "Nariño", 54: "Norte de Santander",
    63: "Quindío", 66: "Risaralda", 68: "Santander", 70: "Sucre", 73: "Tolima", 76: "Valle del Cauca",
    81: "Arauca", 85: "Casanare", 86: "Putumayo", 88: "San Andrés", 91: "Amazonas", 94: "Guainía",
    95: "Guaviare", 97: "Vaupés", 99: "Vichada",
}


def tidy_geo(raw: pd.DataFrame, periodo: str) -> pd.DataFrame:
    df = raw.copy()
    for c in ("monto", "n", "tasa_x_monto"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    cod = pd.to_numeric(df["codigo_municipio"], errors="coerce")
    df["cod_depto"] = (cod // 1000).astype("Int64")
    df["departamento"] = df["cod_depto"].map(DEPARTAMENTOS).fillna("Sin municipio")
    df["deudor_nuevo"] = df["clase_deudor"].astype(str).str.contains("nuevo", case=False)
    df["producto"] = df["producto_de_cr_dito"].map(dict(zip(PRODUCTOS_TASAS,
                                                         ["ingreso_hasta_2_smmlv", "ingreso_superior_2_smmlv", "empresarial"])))
    out = (df.groupby(["departamento", "cod_depto", "producto", "deudor_nuevo"], as_index=False, dropna=False)
           [["monto", "n", "tasa_x_monto"]].sum())
    out["trimestre"] = periodo
    return out


# Nombres legibles por (tipo, código) SFC. El código es estable aunque la entidad cambie de nombre.
NOMBRES = {
    (1, 1): "Banco de Bogotá", (1, 2): "Banco Popular", (1, 6): "Itaú", (1, 7): "Bancolombia",
    (1, 9): "Citibank", (1, 12): "GNB Sudameris", (1, 13): "BBVA", (1, 23): "Banco de Occidente",
    (1, 30): "Caja Social", (1, 39): "Davivienda", (1, 42): "Davibank (antes Scotiabank Colpatria)",
    (1, 43): "Banco Agrario", (1, 49): "AV Villas", (1, 51): "Ban100 (antes Procredit)", (1, 53): "Banco W",
    (1, 54): "Bancoomeva", (1, 55): "Finandina", (1, 56): "Banco Falabella", (1, 57): "Pichincha",
    (1, 58): "Coopcentral", (1, 63): "Serfinanza", (1, 65): "Lulo Bank", (1, 67): "Banco Unión",
    (4, 26): "Tuya", (4, 46): "Coltefinanciera", (4, 121): "Juriscoop", (4, 128): "Nu Financiera",
    (32, 2): "JFK Cooperativa", (32, 5): "Confiar",
}


def etiquetar(df: pd.DataFrame) -> pd.DataFrame:
    """Reemplaza ``entidad`` por el nombre legible cuando el código está en ``NOMBRES``."""
    d = df.copy()
    claves = list(zip(d["tipo_entidad"].astype(int), d["codigo_entidad"].astype(int)))
    d["entidad"] = [NOMBRES.get(k, e) for k, e in zip(claves, d["entidad"])]
    return d


ABREVIATURAS = [
    ("BANCO ", ""), (" S.A.", ""), (" S. A.", ""), (" SA", ""), ("COMPAÑIA DE FINANCIAMIENTO", "CF"),
    ("COMPAÑÍA DE FINANCIAMIENTO", "CF"), ("COOPERATIVA FINANCIERA", "Coop."),
]


def nombre_corto(nombre: str) -> str:
    if not isinstance(nombre, str):
        return nombre
    n = " ".join(nombre.split())
    up = n.upper()
    for a, b in ABREVIATURAS:
        i = up.find(a)
        if i >= 0:
            n = n[:i] + b + n[i + len(a):]
            up = n.upper()
    n = n.strip(" .,")
    return n.title() if n.isupper() else n


# --------------------------------------------------------------------------- carga e indicadores
def cargar(destino: Path) -> dict:
    destino = Path(destino)
    out = {
        "tarjetas": etiquetar(pd.read_csv(destino / "sfc_tarjetas_entidad_mes.csv.gz", parse_dates=["fecha"])),
        "cartera": etiquetar(pd.read_csv(destino / "sfc_cartera_consumo_mora.csv.gz", parse_dates=["fecha"])),
        "tibc": pd.read_csv(destino / "sfc_tibc.csv.gz", parse_dates=["desde", "hasta"]),
        "desembolsos": etiquetar(pd.read_csv(destino / "sfc_desembolsos_tarjeta.csv.gz", parse_dates=["semana"])),
        "geo": pd.read_csv(destino / "sfc_desembolsos_tarjeta_departamento.csv.gz"),
        "meta": json.loads((destino / "metadatos.json").read_text(encoding="utf-8")),
    }
    return out


def cargar_crudo(destino: Path) -> dict:
    destino = Path(destino)
    return {
        "tarjetas": pd.read_csv(destino / "sfc_tarjetas_entidad_mes.csv.gz", usecols=["fecha"]),
        "cartera": pd.read_csv(destino / "sfc_cartera_consumo_mora.csv.gz", usecols=["fecha"]),
        "desembolsos": pd.read_csv(destino / "sfc_desembolsos_tarjeta.csv.gz", usecols=["semana"]),
    }


def _div(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(b > 0, a / b, np.nan)


def indicadores_mora(cartera: pd.DataFrame) -> pd.DataFrame:
    """Indicadores de mora por saldo. En consumo, la SFC considera vencida la cartera con más de 30 días."""
    c = cartera.copy()
    c["mora30"] = c[["mora_30_60", "mora_60_90", "mora_90_180", "mora_180_mas"]].sum(axis=1)
    c["mora60"] = c[["mora_60_90", "mora_90_180", "mora_180_mas"]].sum(axis=1)
    c["mora90"] = c[["mora_90_180", "mora_180_mas"]].sum(axis=1)
    c["icv30"] = _div(c["mora30"], c["saldo"])
    c["icv60"] = _div(c["mora60"], c["saldo"])
    c["icv90"] = _div(c["mora90"], c["saldo"])
    c["calidad_cde"] = _div(c[["saldo_C", "saldo_D", "saldo_E"]].sum(axis=1), c["saldo"])
    # Diferencia entre lo que reporta como vigente + vencido y el saldo (control de consistencia).
    c["descuadre"] = _div((c["vigente"] + c["mora30"] - c["saldo"]).abs(), c["saldo"])
    return c


def agregar_mercado(df: pd.DataFrame, por: list[str], sumas: list[str]) -> pd.DataFrame:
    return df.groupby(por, as_index=False)[sumas].sum()


def indicadores_tarjeta(t: pd.DataFrame) -> pd.DataFrame:
    """Indicadores derivados de h2jg por fila (entidad-mes o mercado-mes)."""
    d = t.copy()
    for c in set(METRICAS_TARJETA.values()) | {"tarjetas_vigentes_juridica"}:
        if c not in d.columns:
            d[c] = np.nan
    d["utilizacion"] = _div(d["saldo_tarjeta"], d["saldo_tarjeta"] + d["cupo_no_utilizado"])
    d["cupo_promedio"] = _div(d["saldo_tarjeta"] + d["cupo_no_utilizado"], d["tarjetas_vigentes"])
    d["saldo_por_tarjeta"] = _div(d["saldo_tarjeta"], d["tarjetas_vigentes"])
    d["peso_avances_monto"] = _div(d["monto_avances"], d["monto_avances"] + d["monto_compras"])
    d["ticket_compra"] = _div(d["monto_compras"], d["n_compras"])
    d["ticket_avance"] = _div(d["monto_avances"], d["n_avances"])
    d["compras_por_tarjeta"] = _div(d["n_compras"], d["tarjetas_vigentes"])
    d["participacion_juridica"] = _div(d["tarjetas_vigentes_juridica"], d["tarjetas_vigentes"])
    return d


def anualizar_flujo(df: pd.DataFrame, flujo: str, saldo: str, por: list[str]) -> pd.Series:
    """Flujo de 12 meses / saldo promedio de 12 meses, calculado dentro de cada grupo ``por``.

    Requiere 12 meses consecutivos; con huecos devuelve NaN.
    """
    d = df.sort_values(por + ["fecha"]).copy()
    g = d.groupby(por, group_keys=False)
    f12 = g[flujo].apply(lambda s: s.rolling(12, min_periods=12).sum())
    s12 = g[saldo].apply(lambda s: s.rolling(12, min_periods=12).mean())
    meses = g["fecha"].apply(lambda s: (s.dt.year * 12 + s.dt.month).diff(11))
    r = pd.Series(_div(f12, s12), index=d.index)
    r[meses != 11] = np.nan
    return r.reindex(df.index)


def hhi(participaciones: pd.Series) -> float:
    """Índice Herfindahl-Hirschman en escala 0-10.000."""
    s = participaciones / participaciones.sum()
    return float((s.pow(2) * 10_000).sum())


def percentil_en_mercado(valor: float, distribucion: pd.Series, pesos: pd.Series | None = None) -> float:
    """Percentil (0-1) de ``valor`` dentro de la distribución de entidades, ponderada si hay pesos."""
    x = pd.Series(distribucion, dtype=float).dropna()
    w = pd.Series(1.0, index=x.index) if pesos is None else pd.Series(pesos, dtype=float).reindex(x.index).fillna(0)
    if w.sum() == 0:
        return np.nan
    return float(w[x < valor].sum() / w.sum() + 0.5 * w[x == valor].sum() / w.sum())


def perfil_mora_por_edad(ever_mob: np.ndarray, roll_off: float) -> np.ndarray:
    """Fracción del saldo de una cosecha que está en mora >30 a cada edad.

    ever_mob[k] = fracción del saldo que ha entrado a mora a la edad k+1 (curva EVER acumulada).
    El saldo en mora sale del balance (castigo o cura) a tasa mensual ``roll_off``.
    """
    ever = np.asarray(ever_mob, dtype=float)
    entradas = np.diff(np.r_[0.0, ever])
    return np.array([sum(entradas[k] * (1 - roll_off) ** (a - k) for k in range(a + 1)) for a in range(len(ever))])


def mora_stock_estacionaria(ever_mob: np.ndarray, roll_off: float, crecimiento_mensual: float = 0.0) -> float:
    """Mora >30 de stock en estado estacionario implicada por una curva de entrada a mora.

    Conecta la medida de cosecha (EVER) con la de stock que publica la SFC. Supuestos:
    originación que crece a tasa ``crecimiento_mensual``, saldo al día que no amortiza y
    salida mensual ``roll_off`` del saldo en mora. Es una aproximación de orden de magnitud,
    no una conversión exacta.

    El crecimiento pesa más las cosechas jóvenes. Baja el stock cuando la mora por edad sube
    con la edad (salida lenta) y lo sube cuando la mora se concentra en edades tempranas y
    sale rápido. ``perfil_mora_por_edad`` muestra cuál de los dos casos aplica.
    """
    perfil = perfil_mora_por_edad(ever_mob, roll_off)
    edades = np.arange(1, len(perfil) + 1, dtype=float)
    peso = (1.0 + float(crecimiento_mensual)) ** (-edades)
    return float((peso * perfil).sum() / peso.sum())


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "datos_publicos"
    if "--solo-geo" in sys.argv:  # rehace solo la vista territorial y los metadatos
        d = cargar_crudo(destino)
        q = pd.Period(sys.argv[sys.argv.index("--solo-geo") + 1], "Q")
        descargar_geo(q).to_csv(destino / "sfc_desembolsos_tarjeta_departamento.csv.gz", index=False)
        print(escribir_metadatos(destino, d["tarjetas"], d["cartera"], d["desembolsos"], str(q)))
    else:
        print(json.dumps(descargar(destino), ensure_ascii=False, indent=2))
    sys.exit(0)
