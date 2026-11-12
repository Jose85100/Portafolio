"""Observed-rate sensitivity for an explicitly hypothetical project covenant."""
from pathlib import Path
import hashlib
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parents[4] / "04-quant-strategy-and-products/treasury-and-alm/sensibilidad-fondeo-dtf/data/dtf_monthly_derived.csv"
OUT = BASE / "results"
EXPECTED_SHA256 = "56e4e436cd7add0aac50dd8e1c29007fa173ed8e07e4b484633d19faa33c79ec"
BALANCE_COP_MM = 100_000.0
CFADS_COP_MM = 15_000.0
BASE_DEBT_SERVICE_COP_MM = 11_000.0
COVENANT_DSCR = 1.20


def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("La huella del derivado DTF no coincide con el snapshot documentado")
    df = pd.read_csv(SOURCE)
    df["mes"] = pd.to_datetime(df["mes"], format="%Y-%m")
    df = df[(df.mes >= "2010-01-01") & (df.mes <= "2026-09-01")].copy()
    expected = pd.date_range("2010-01-01", "2026-09-01", freq="MS")
    if df.mes.duplicated().any() or not df.mes.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("El calendario DTF tiene meses duplicados o faltantes")
    if not df.dtf_promedio.map(math.isfinite).all() or not (df.observaciones_dtf == df.mes.dt.days_in_month).all():
        raise ValueError("La muestra contiene tasas no finitas o meses incompletos")
    df["delta_dtf_12m_pp"] = df.dtf_promedio.diff(12)
    # Cambio anualizado de intereses si todo el saldo hipotético repricia 1:1.
    df["delta_interes_anual_cop_mm"] = BALANCE_COP_MM * df.delta_dtf_12m_pp / 100
    df["debt_service_sensitivity_cop_mm"] = BASE_DEBT_SERVICE_COP_MM + df.delta_interes_anual_cop_mm
    df["dscr_sensitivity"] = CFADS_COP_MM / df.debt_service_sensitivity_cop_mm
    df["headroom_to_covenant_cop_mm"] = (
        CFADS_COP_MM / COVENANT_DSCR - df.debt_service_sensitivity_cop_mm
    )
    usable = df.dropna(subset=["delta_dtf_12m_pp"])
    latest = usable.iloc[-1]
    max_rate_shock_pp = (
        (CFADS_COP_MM / COVENANT_DSCR - BASE_DEBT_SERVICE_COP_MM) / BALANCE_COP_MM * 100
    )
    result = {
        "source_sha256": digest, "source_relative_path": "04-quant-strategy-and-products/treasury-and-alm/sensibilidad-fondeo-dtf/data/dtf_monthly_derived.csv",
        "source_window": ["2010-01", "2026-09"], "months": len(df),
        "hypothetical_balance_cop_mm": BALANCE_COP_MM, "hypothetical_cfads_cop_mm": CFADS_COP_MM,
        "hypothetical_base_debt_service_cop_mm": BASE_DEBT_SERVICE_COP_MM,
        "hypothetical_covenant_dscr": COVENANT_DSCR,
        "max_positive_rate_shock_before_covenant_breach_pp": max_rate_shock_pp,
        "latest_month": latest.mes.strftime("%Y-%m"), "latest_observed_dtf_pct_ea": float(latest.dtf_promedio),
        "latest_observed_12m_change_pp": float(latest.delta_dtf_12m_pp),
        "latest_mechanical_interest_change_cop_mm_annualized": float(latest.delta_interes_anual_cop_mm),
        "latest_sensitivity_dscr": float(latest.dscr_sensitivity),
        "latest_headroom_to_covenant_cop_mm_annualized": float(latest.headroom_to_covenant_cop_mm),
        "interpretation": "Sensibilidad condicional ilustrativa; no es forecast, probabilidad de breach ni covenant de proyecto real."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "dtf_covenant_sensitivity.csv", index=False, date_format="%Y-%m")
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True, constrained_layout=True)
    axes[0].plot(df.mes, df.delta_dtf_12m_pp, color="#176b87", linewidth=1.4)
    axes[0].axhline(max_rate_shock_pp, color="#b5483a", linestyle="--", label=f"Umbral mecánico covenant: +{max_rate_shock_pp:.2f} pp")
    axes[0].axhline(0, color="gray", linewidth=.7)
    axes[0].set_ylabel("Cambio DTF 12m (pp)")
    axes[0].legend(loc="upper left", frameon=False)
    axes[0].set_title("Choque observado de DTF y sensibilidad de covenant hipotético")
    axes[1].plot(df.mes, df.dscr_sensitivity, color="#d08436", linewidth=1.4)
    axes[1].axhline(COVENANT_DSCR, color="#b5483a", linestyle="--", label=f"Covenant ilustrativo: {COVENANT_DSCR:.2f}x")
    axes[1].set_ylabel("DSCR mecánico (x)")
    axes[1].legend(loc="upper left", frameon=False)
    fig.savefig(OUT / "dtf_covenant_sensitivity.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
