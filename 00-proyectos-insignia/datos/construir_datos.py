"""Capa de datos compartida de los proyectos insignia.

Descarga (opcional) y normaliza cinco fuentes públicas oficiales:

  * SFC, cartera por calificación y altura de mora (datos.gov.co rvii-eis8), mensual 2015-2026.
  * SFC, tasas activas y desembolsos semanales por entidad y producto (yvb2-ppaa), 2002-2022.
  * SFC, interés bancario corriente por modalidad (pare-7x5i); usura = 1,5 x IBC.
  * BanRep, tasa de política monetaria (serie 59 de SUAMECA), diaria.
  * DANE, GEIH (tasa de desocupación nacional mensual), IPC e ISE.

Uso:
    python3 construir_datos.py --descargar   # baja los crudos a datos/raw (no versionados)
    python3 construir_datos.py               # reconstruye datos/procesados y el manifiesto

Los crudos de datos.gov.co pesan ~350 MB y no se versionan; el manifiesto guarda su
SHA-256, la URL y la fecha de extracción para reproducir el corte.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAW = AQUI / "raw"
OUT = AQUI / "procesados"
REPO = AQUI.parents[1]

SOCRATA = "https://www.datos.gov.co/resource/{id}.json?$limit=50000&$offset={off}&$order=:id"
FUENTES = {
    "rvii": {"id": "rvii-eis8", "filas": 112_602, "nombre": "SFC - Cartera por calificación y mora por entidad y producto"},
    "yvb2": {"id": "yvb2-ppaa", "filas": 732_673, "nombre": "SFC - Tasas de interés activas y montos desembolsados semanales"},
}
URL_USURA = "https://www.datos.gov.co/resource/pare-7x5i.json?$limit=1000"
URL_TPM = ("https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/estadisticaEconomicaRestService/"
           "consultaInformacionSerieXTipoDato?idSerie=59&tipoDato=0&cantDatos=20000")
URL_GEIH = "https://www.dane.gov.co/files/operaciones/GEIH/anex-GEIH-sep2026.xlsx"
IPC_CSV = REPO / "02-mathematics-statistics-and-quant/quantitative-methods/arima-pronostico/reports/dane_ipc_monthly_extracted.csv"
ISE_CSV = REPO / "01-economics-and-econometrics/01-macroeconomics/06-macro-regime-switching/reports/ise_sign_regimes_monthly.csv"

# Familias de producto para los análisis (unicap de la SFC).
FAMILIA = {
    "1": "Consumo", "2": "Consumo", "3": "Consumo", "4": "Consumo", "5": "Consumo", "6": "Consumo",
    "29": "Consumo", "30": "Consumo",
    "7": "Microcrédito", "8": "Microcrédito",
    **{str(k): "Vivienda" for k in range(9, 19)}, "31": "Vivienda", "32": "Vivienda",
    **{str(k): "Comercial" for k in range(19, 29)},
}
PRODUCTO_CORTO = {
    "1": "Rotativo", "2": "Tarjeta de crédito", "3": "Libre inversión", "4": "Libranza", "5": "Vehículo",
    "6": "Otros consumo", "29": "Consumo bajo monto", "30": "Consumo empleados",
    "7": "Microcrédito <=25 SMMLV", "8": "Microcrédito 25-120 SMMLV",
}
TIPO_ENTIDAD = {"1": "Banco", "2": "Corporación financiera", "4": "Compañía de financiamiento",
                "22": "Instituciones oficiales especiales", "32": "Cooperativa financiera"}

# Columnas de altura de mora. Vencida >= 90 días: buckets que arrancan en el mes 3 o después.
# En vivienda el primer bucket es 1-4 meses, así que su mora90 es en realidad >120 días (más estricta).
VENCIDA = ["_3_vencida_1_2_meses", "_4_vencida_2_3_meses", "_5_vencida_1_3_meses", "_6_vencida_3_4_meses",
           "_7_vencida_de_4_meses", "_8_vencida_3_6_meses", "_9_vencida_6_meses", "_10_vencida_1_4_meses",
           "_11_vencida_4_6_meses", "_12_vencida_6_12_meses", "_13_vencida_12_18_meses", "_14_vencida_12_meses",
           "_15_vencida_18_meses"]
VENCIDA_90 = ["_6_vencida_3_4_meses", "_7_vencida_de_4_meses", "_8_vencida_3_6_meses", "_9_vencida_6_meses",
              "_11_vencida_4_6_meses", "_12_vencida_6_12_meses", "_13_vencida_12_18_meses",
              "_14_vencida_12_meses", "_15_vencida_18_meses"]
CALIF = {"A": ("_17", "_18"), "B": ("_19", "_20"), "C": ("_21", "_22"), "D": ("_23", "_24"), "E": ("_25", "_26")}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def descargar() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for clave, meta in FUENTES.items():
        for off in range(0, meta["filas"] + 50_000, 50_000):
            url = SOCRATA.format(id=meta["id"], off=off)
            subprocess.run(["curl", "-sf", "--max-time", "300", url, "-o", str(RAW / f"{clave}_{off}.json")], check=True)
    subprocess.run(["curl", "-sf", URL_USURA, "-o", str(RAW / "pare_usura.json")], check=True)
    subprocess.run(["curl", "-sf", URL_TPM, "-o", str(RAW / "banrep_tpm_59.json")], check=True)
    subprocess.run(["curl", "-sf", URL_GEIH, "-o", str(RAW / "geih_sep2026.xlsx")], check=True)


def _leer_partes(prefijo: str) -> pd.DataFrame:
    partes = sorted(glob.glob(str(RAW / f"{prefijo}_*.json")))
    df = pd.concat([pd.DataFrame(json.load(open(p))) for p in partes], ignore_index=True)
    return df


def construir_cartera() -> pd.DataFrame:
    r = _leer_partes("rvii")
    assert len(r) == FUENTES["rvii"]["filas"], f"rvii: {len(r)} filas"
    # Una fila total por producto: la tarjeta, construcción, leasing y libranza traen subrenglones.
    total = r["desc_renglon"].str.upper().str.contains("TOTAL") | ~r["unicap"].isin(["2", "4", "27", "28"])
    r = r[total].copy()
    num = [c for c in r.columns if c.startswith("_")]
    r[num] = r[num].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    out = pd.DataFrame({
        "mes": pd.to_datetime(r["fecha_corte"]).dt.to_period("M").astype(str),
        "tipo_entidad": r["tipo_entidad"].map(TIPO_ENTIDAD).fillna("Otro"),
        "codigo_entidad": r["tipo_entidad"] + "-" + r["codigo_entidad"],
        "entidad": r["nombreentidad"].str.strip(),
        "unicap": r["unicap"],
        "producto": r["unicap"].map(PRODUCTO_CORTO).fillna(r["descrip_uc"].str.title()),
        "familia": r["unicap"].map(FAMILIA),
        "saldo": r["_1_saldo_de_la_cartera_a"],
        "vigente": r["_2_vigente"],
        "mora30": r[VENCIDA].sum(axis=1),
        "mora90": r[VENCIDA_90].sum(axis=1),
        "mora_1_2m": r["_3_vencida_1_2_meses"],
        "clientes_mora": r["_16_n_mero_de_clientes_mora"],
    })
    for k, (n, s) in CALIF.items():
        out[f"n_{k}"] = r[f"{n}_calificaci_n_de_riesgo"].values
        out[f"saldo_{k}"] = r[f"{s}_calificaci_n_de_riesgo"].values
    # Duplicados: algunas entidades reportan dos renglones TOTAL con grafías distintas; se suman no, se deduplican.
    out = (out.sort_values("saldo", ascending=False)
              .drop_duplicates(["mes", "codigo_entidad", "unicap"]).sort_values(["mes", "codigo_entidad", "unicap"]))
    out = out[out["saldo"] > 0]
    # Control: vigente + vencida debe reconciliar con el saldo.
    rec = (out["vigente"] + out["mora30"]) / out["saldo"]
    out["reconcilia"] = (rec - 1).abs() < 0.01
    return out.reset_index(drop=True)


def construir_tasas() -> pd.DataFrame:
    y = _leer_partes("yvb2")
    assert len(y) == FUENTES["yvb2"]["filas"], f"yvb2: {len(y)} filas"
    credito = ~y["nombre"].isin(["CERTIFICADOS AHORRO VLOR REAL (CAVR)", "DEPOSITOS Y CUENTAS DE AHORRO", "SIN DATOS"])
    y = y[credito].copy()
    y["tipo"] = y["tipo"].str.replace("ADQUISICIÃ“N", "ADQUISICIÓN", regex=False)
    out = pd.DataFrame({
        "semana": pd.to_datetime(y["fechacorte"]).dt.date.astype(str),
        "codigo_entidad": y["tipoentidad"] + "-" + y["codigoentidad"],
        "entidad": y["nombreentidad"].str.strip(),
        "modalidad": y["nombre"], "tipo": y["tipo"], "subcuenta": y["nombre_sub"],
        "tasa_ea": pd.to_numeric(y["tasaefectivaanual"], errors="coerce"),
        "monto": pd.to_numeric(y["montos"], errors="coerce"),
        "n_creditos": pd.to_numeric(y["num_creditos_desembolsados"], errors="coerce"),
    })
    out = out[(out["monto"] > 0) & out["tasa_ea"].between(0.01, 200)]
    return out.sort_values(["semana", "codigo_entidad", "modalidad", "tipo", "subcuenta"]).reset_index(drop=True)


def construir_usura() -> pd.DataFrame:
    p = pd.DataFrame(json.load(open(RAW / "pare_usura.json")))
    p["ibc"] = p["interes_bancario_corriente"].str.replace("%", "").str.replace(",", ".").astype(float)
    p["desde"] = pd.to_datetime(p["vigencia_desde"])
    p["hasta"] = pd.to_datetime(p["vigencia_hasta"])
    p = p.sort_values(["modalidad", "desde"])
    p["usura"] = 1.5 * p["ibc"]
    return p[["modalidad", "resolucion", "desde", "hasta", "ibc", "usura"]].reset_index(drop=True)


def construir_macro() -> pd.DataFrame:
    t = json.load(open(RAW / "banrep_tpm_59.json"))[0]
    tpm = pd.DataFrame(t["data"], columns=["ms", "tpm"])
    tpm["mes"] = pd.to_datetime(tpm["ms"], unit="ms").dt.to_period("M").astype(str)
    tpm = tpm.groupby("mes", as_index=False)["tpm"].mean()

    g = pd.read_excel(RAW / "geih_sep2026.xlsx", "Total nacional", header=None)
    anios = g.iloc[11, 1:].ffill()
    meses = g.iloc[12, 1:]
    fila = g.index[g[0].astype(str).str.startswith("Tasa de Desocupaci")][0]
    nombres = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Sep": 9,
               "Oct": 10, "Nov": 11, "Dic": 12}
    td = pd.DataFrame({"anio": anios.values, "m": meses.values, "desempleo": g.iloc[fila, 1:].values}).dropna()
    td["mes"] = [f"{int(float(str(a)[:4]))}-{nombres[str(m).strip()[:3].title()]:02d}" for a, m in zip(td.anio, td.m)]
    td = td[["mes", "desempleo"]].astype({"desempleo": float})

    ipc = pd.read_csv(IPC_CSV).rename(columns={"month": "mes"})
    ipc["inflacion"] = 100 * (ipc["ipc_total_nacional"] / ipc["ipc_total_nacional"].shift(12) - 1)
    ise = pd.read_csv(ISE_CSV).rename(columns={"date": "mes", "ise_yoy_growth_pct": "ise_crec"})[["mes", "ise_crec"]]

    m = tpm.merge(td, on="mes", how="outer").merge(ipc[["mes", "inflacion"]], on="mes", how="outer").merge(ise, on="mes", how="outer")
    m = m.sort_values("mes")
    m["desempleo_12m"] = m["desempleo"].rolling(12, min_periods=12).mean()
    return m[m["mes"] >= "2005-01"].reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", action="store_true")
    args = ap.parse_args()
    if args.descargar:
        descargar()
    OUT.mkdir(exist_ok=True)
    salidas = {
        "cartera_sfc_mensual.csv.gz": construir_cartera(),
        "tasas_desembolsos_semanal.csv.gz": construir_tasas(),
        "usura_por_modalidad.csv": construir_usura(),
        "macro_mensual.csv": construir_macro(),
    }
    for nombre, df in salidas.items():
        df.to_csv(OUT / nombre, index=False, compression="gzip" if nombre.endswith(".gz") else None)
    manifiesto = {
        "fecha_extraccion": "2026-11-12",
        "fecha_construccion": str(date.today()),
        "fuentes": {
            "rvii-eis8": {**FUENTES["rvii"], "url": "https://www.datos.gov.co/resource/rvii-eis8.json"},
            "yvb2-ppaa": {**FUENTES["yvb2"], "url": "https://www.datos.gov.co/resource/yvb2-ppaa.json"},
            "pare-7x5i": {"nombre": "SFC - Interés bancario corriente por modalidad", "url": URL_USURA},
            "banrep-59": {"nombre": "BanRep - Tasa de política monetaria", "url": URL_TPM},
            "dane-geih": {"nombre": "DANE - GEIH anexo sep-2026, Total nacional", "url": URL_GEIH},
            "dane-ipc": {"nombre": "DANE - IPC total nacional (derivado del repositorio)", "ruta": str(IPC_CSV.relative_to(REPO))},
            "dane-ise": {"nombre": "DANE - ISE, variación anual (derivado del repositorio)", "ruta": str(ISE_CSV.relative_to(REPO))},
        },
        "crudos_sha256": {Path(p).name: sha256(Path(p)) for p in sorted(glob.glob(str(RAW / "*")))},
        "procesados": {n: {"filas": int(len(df)), "sha256": sha256(OUT / n)} for n, df in salidas.items()},
    }
    (OUT / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False))
    for n, df in salidas.items():
        print(f"{n}: {len(df):,} filas")


if __name__ == "__main__":
    main()
