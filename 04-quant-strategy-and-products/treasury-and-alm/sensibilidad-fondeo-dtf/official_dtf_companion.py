"""Contexto de sensibilidad de fondeo con DTF mensual derivada del Atlas."""
from pathlib import Path
import hashlib
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "data/dtf_monthly_derived.csv"
OUT = BASE / "reports"
EXPECTED_SHA256 = "56e4e436cd7add0aac50dd8e1c29007fa173ed8e07e4b484633d19faa33c79ec"

def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("La huella del derivado DTF no coincide con el snapshot")
    df = pd.read_csv(SOURCE)
    df["mes"] = pd.to_datetime(df["mes"], format="%Y-%m")
    if df["mes"].duplicated().any() or not df["mes"].is_monotonic_increasing:
        raise ValueError("Meses duplicados o desordenados")
    # Octubre es parcial en el archivo del Atlas; no se emplea como mes cerrado.
    df = df[(df.mes >= "2010-01-01") & (df.mes <= "2026-09-01")].copy()
    expected = pd.date_range("2010-01-01", "2026-09-01", freq="MS")
    if not df.mes.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("Falta algún mes cerrado")
    if not df.dtf_promedio.map(math.isfinite).all() or not (df.observaciones_dtf == df.mes.dt.days_in_month).all():
        raise ValueError("DTF incompleta en el periodo de análisis")
    df["delta_12m_pp"] = df.dtf_promedio.diff(12)
    # Costo anualizado de sensibilidad para saldo hipotético constante COP 100.000 millones.
    df["delta_cost_cop_millones_anualizado"] = 100000 * df.delta_12m_pp / 100
    usable = df.dropna(subset=["delta_12m_pp"])
    last = usable.iloc[-1]
    result = {"source_drive_id": "1Hpu_qk99U_-Hf0H3svT2GvVYWtb9EfpE", "derived_sha256": digest,
              "start": "2010-01", "end": "2026-09", "months": len(df),
              "hypothetical_balance_cop_millions": 100000,
              "last_dtf_percent": float(last.dtf_promedio), "last_delta_12m_pp": float(last.delta_12m_pp),
              "last_sensitivity_cop_millions_annualized": float(last.delta_cost_cop_millones_anualizado),
              "min_delta_12m_pp": float(usable.delta_12m_pp.min()), "max_delta_12m_pp": float(usable.delta_12m_pp.max())}
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "dtf_funding_sensitivity.csv", index=False, date_format="%Y-%m")
    (OUT / "dtf_funding_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True, constrained_layout=True)
    axes[0].plot(df.mes, df.dtf_promedio, color="#164a70")
    axes[0].set(title="DTF mensual: contexto de fondeo", ylabel="% efectivo anual")
    axes[1].plot(df.mes, df.delta_cost_cop_millones_anualizado, color="#bf6743")
    axes[1].axhline(0, color="gray", linewidth=.7)
    axes[1].set(title="Sensibilidad anualizada de saldo hipotético COP 100.000 millones", ylabel="COP millones / año")
    fig.savefig(OUT / "dtf_funding_sensitivity.png", dpi=150)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
