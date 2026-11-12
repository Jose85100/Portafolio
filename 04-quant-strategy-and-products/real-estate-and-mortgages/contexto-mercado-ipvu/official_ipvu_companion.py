#!/usr/bin/env python3
"""Reproduce a descriptive market-context proxy from BanRep's official IPVU."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
SOURCES = {
    "nominal": (DATA / "ipvu-banrep-2026-11-10-latest.json", "2685543dd6ca23680aacd736cfb5078c163b36eda763b6b1708ff61a23de0ec4", 56),
    "real": (DATA / "ipvu-real-banrep-2026-11-10.json", "46d19dfcceac2ad0107cc0167809bd80be99089273615e784716d185d7ba0311", 57),
}


def load_series(path: Path, expected_sha: str, expected_id: int) -> pd.Series:
    raw = path.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != expected_sha:
        raise ValueError(f"SHA-256 inesperado para {path.name}: {actual_sha}")
    payload = json.loads(raw)
    if len(payload) != 1 or payload[0].get("id") != expected_id:
        raise ValueError(f"Metadatos inesperados en {path.name}")
    item = payload[0]
    observations = item.get("data", [])
    idx = pd.to_datetime([row[0] for row in observations], unit="ms", utc=True).tz_convert(None)
    values = [float(row[1]) for row in observations]
    result = pd.Series(values, index=idx, name="real" if expected_id == 57 else "nominal")
    result.index = result.index.to_period("Q").to_timestamp(how="end").normalize()
    if result.index.has_duplicates or len(result) != 154:
        raise ValueError(f"Número de observaciones o fechas duplicadas en {path.name}")
    if item.get("fechaFinal") != "30 de junio  de  2026":
        raise ValueError(f"Corte inesperado: {item.get('fechaFinal')}")
    return result


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    nominal = load_series(*SOURCES["nominal"][:2], SOURCES["nominal"][2])
    real = load_series(*SOURCES["real"][:2], SOURCES["real"][2])
    if not nominal.index.equals(real.index):
        raise ValueError("Las series nominal y real no tienen el mismo calendario")
    frame = pd.concat([nominal, real], axis=1)
    frame["real_yoy_pct"] = 100 * (frame["real"] / frame["real"].shift(4) - 1)
    frame.index.name = "quarter_end"
    frame.to_csv(REPORTS / "ipvu_quarterly_derived.csv", float_format="%.6f")

    analysis = frame.loc["2015-03-31":"2026-06-30", "real_yoy_pct"].dropna()
    sensitivity = frame.loc["2010-03-31":"2026-06-30", "real_yoy_pct"].dropna()
    quantiles = analysis.quantile([0.10, 0.50, 0.90])
    latest = float(frame["real_yoy_pct"].iloc[-1])
    summary = {
        "source": "Banco de la República (BanRep), IPVU nominal y real, datos trimestrales",
        "source_api": "https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/estadisticaEconomicaRestService/consultaInformacionSerieXTipoDato?idSerie={56|57}&tipoDato=0&cantDatos=300",
        "source_page": "https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/100004/indice_precios_vivienda_usada_ipvu/",
        "vintage_downloaded": "2026-11-10",
        "source_last_loaded": "2026-10-23",
        "latest_observation": "2026-Q2",
        "grain": "national quarterly index; base 1990=100",
        "observations": len(frame),
        "real_yoy_formula": "100 * (real_index_t / real_index_t_minus_4 - 1)",
        "window_primary": "2015-Q1 to 2026-Q2; YoY requires four-quarter lag",
        "window_sensitivity": "2010-Q1 to 2026-Q2",
        "latest_real_yoy_pct": latest,
        "primary_n_yoy": int(analysis.size),
        "primary_yoy_quantiles_pct": {f"p{int(q*100)}": float(v) for q, v in quantiles.items()},
        "sensitivity_n_yoy": int(sensitivity.size),
        "sensitivity_yoy_quantiles_pct": {f"p{int(q*100)}": float(v) for q, v in sensitivity.quantile([.1,.5,.9]).items()},
        "sha256": {key: spec[1] for key, spec in SOURCES.items()},
        "decision_use": "referencia descriptiva para enmarcar escenarios de mercado y priorizar revisión humana; no estima valor de un inmueble ni rentabilidad de una inversión",
    }
    (REPORTS / "ipvu_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True, constrained_layout=True)
    axes[0].plot(frame.index, frame["nominal"], color="#4C78A8", lw=1.8)
    axes[0].set_title("IPVU nominal (índice oficial; base 1990=100)")
    axes[0].set_ylabel("Índice")
    axes[1].plot(frame.index, frame["real"], color="#F58518", lw=1.8)
    axes[1].set_title("IPVU real (índice oficial; base 1990=100)")
    axes[1].set_ylabel("Índice")
    axes[2].plot(frame.index, frame["real_yoy_pct"], color="#2A6F62", lw=1.7)
    for q, color in [(0.10, "#E45756"), (0.50, "#777777"), (0.90, "#E45756")]:
        axes[2].axhline(analysis.quantile(q), color=color, lw=1, ls="--", alpha=.8, label=f"p{int(q*100)} ventana 2015–2026")
    axes[2].scatter(frame.index[-1], latest, color="#7A5195", zorder=5)
    axes[2].annotate(f"2026-Q2: {latest:.1f}%", (frame.index[-1], latest), xytext=(-8, 9), textcoords="offset points", ha="right", fontsize=9)
    axes[2].set_title("Variación interanual del IPVU real")
    axes[2].set_ylabel("% interanual")
    axes[2].set_xlabel("Fecha trimestral")
    axes[2].legend(frameon=False, ncol=3, fontsize=8)
    fig.suptitle("BanRep IPVU: contexto observado del mercado de vivienda usada", fontsize=14, weight="bold")
    fig.text(.01, -.005, "Índices agregados basados en avalúos de garantías hipotecarias; el cambio no es retorno de una cartera ni valorización de un inmueble individual.", fontsize=8)
    fig.savefig(REPORTS / "ipvu_market_context.png", dpi=180, bbox_inches="tight")
    print(json.dumps({"latest_real_yoy_pct": latest, "primary_yoy_quantiles_pct": summary["primary_yoy_quantiles_pct"], "observations": len(frame)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
