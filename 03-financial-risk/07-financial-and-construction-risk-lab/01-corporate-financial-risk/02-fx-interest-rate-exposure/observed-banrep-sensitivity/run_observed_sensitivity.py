#!/usr/bin/env python3
"""Descriptive market-factor sensitivity for explicitly hypothetical exposures."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
TRM = ROOT / "data/trm-banrep-series-id-1-snapshot-2026-11-11.json"
DTF = ROOT.parents[4] / "04-quant-strategy-and-products/treasury-and-alm/sensibilidad-fondeo-dtf/data/dtf_monthly_derived.csv"
OUT = ROOT / "results"
TRM_SHA256 = "d5068f3801b18a5530d291d6a2d0587e5ceb580d52879de5ae363168999edf77"
DTF_SHA256 = "56e4e436cd7add0aac50dd8e1c29007fa173ed8e07e4b484633d19faa33c79ec"
USD_LIABILITY = 1_000_000
COP_FLOATING_BALANCE = 100_000_000_000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_trm() -> pd.DataFrame:
    if sha(TRM) != TRM_SHA256:
        raise ValueError("Hash de snapshot TRM inesperado")
    payload = json.loads(TRM.read_text(encoding="utf-8"))
    if len(payload) != 1 or payload[0].get("id") != 1 or payload[0].get("unidad") != "COP/USD":
        raise ValueError("Metadatos de serie TRM inesperados")
    item = payload[0]
    rows = item.get("data", [])
    dates = pd.to_datetime([x[0] for x in rows], unit="ms", utc=True).tz_convert("America/Bogota").tz_localize(None).normalize()
    frame = pd.DataFrame({"fecha": dates, "trm_cop_usd": [float(x[1]) for x in rows]})
    if frame.fecha.duplicated().any() or not frame.fecha.is_monotonic_increasing or not frame.trm_cop_usd.map(math.isfinite).all():
        raise ValueError("Fechas o valores TRM inválidos")
    # Último dato oficial disponible de cada mes (no un promedio mensual).
    frame["mes"] = frame.fecha.dt.to_period("M").dt.to_timestamp()
    month_end = frame.groupby("mes", as_index=False).tail(1).sort_values("mes").reset_index(drop=True)
    month_end["fx_liability_cop"] = USD_LIABILITY * month_end.trm_cop_usd
    month_end["fx_revaluation_change_cop"] = month_end.fx_liability_cop.diff()
    month_end["fx_revaluation_change_cop_millions"] = month_end.fx_revaluation_change_cop / 1e6
    return month_end


def load_dtf() -> pd.DataFrame:
    if sha(DTF) != DTF_SHA256:
        raise ValueError("Hash del derivado DTF inesperado")
    df = pd.read_csv(DTF)
    df["mes"] = pd.to_datetime(df["mes"], format="%Y-%m")
    df = df[(df.mes >= "2010-01-01") & (df.mes <= "2026-09-01")].copy()
    expected = pd.date_range("2010-01-01", "2026-09-01", freq="MS")
    if not df.mes.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("Calendario DTF cerrado incompleto")
    if (df.observaciones_dtf != df.mes.dt.days_in_month).any() or not df.dtf_promedio.map(math.isfinite).all():
        raise ValueError("Observaciones DTF incompletas o no finitas")
    df["delta_dtf_12m_pp"] = df.dtf_promedio.diff(12)
    # Approximation: balance assumed constant; annual interest cost change = balance * rate change.
    df["dtf_annualized_cost_change_cop"] = COP_FLOATING_BALANCE * df.delta_dtf_12m_pp / 100
    df["dtf_annualized_cost_change_cop_millions"] = df.dtf_annualized_cost_change_cop / 1e6
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fx = load_trm()
    dtf = load_dtf()
    # Align each observed market factor by month; results remain separate and are not summed.
    frame = fx.merge(dtf[["mes", "dtf_promedio", "observaciones_dtf", "delta_dtf_12m_pp", "dtf_annualized_cost_change_cop", "dtf_annualized_cost_change_cop_millions"]], on="mes", how="inner", validate="one_to_one")
    frame.to_csv(OUT / "monthly_factor_sensitivities.csv", index=False, date_format="%Y-%m-%d", float_format="%.8f")
    fx_active = frame.dropna(subset=["fx_revaluation_change_cop"])
    dtf_active = frame.dropna(subset=["delta_dtf_12m_pp"])
    latest = frame.iloc[-1]
    summary = {
        "purpose": "Observed market-factor context for hypothetical exposures; not an entity exposure assessment or model validation",
        "source_trm": {"publisher": "Banco de la República", "series_id": 1, "name": "Tasa Representativa del Mercado (TRM)", "unit": "COP/USD", "api": "https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/estadisticaEconomicaRestService/consultaInformacionSerieXTipoDato?idSerie=1&tipoDato=0&cantDatos=5000", "official_series_page": "https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/1/tasa_cambio_peso_colombiano_trm_dolar_usd/", "snapshot_sha256": TRM_SHA256, "snapshot_metadata_start": json.loads(TRM.read_text(encoding="utf-8"))[0].get("fechaInicial"), "snapshot_metadata_end": json.loads(TRM.read_text(encoding="utf-8"))[0].get("fechaFinal"), "monthly_sampling": "last available daily observation in each month"},
        "source_dtf": {"publisher": "Banco de la República via Atlas Económico; governed derived file", "drive_id": "1Hpu_qk99U_-Hf0H3svT2GvVYWtb9EfpE", "derived_file": "../../../../../04-quant-strategy-and-products/treasury-and-alm/sensibilidad-fondeo-dtf/data/dtf_monthly_derived.csv", "derived_sha256": DTF_SHA256, "method": "monthly mean, only complete months through 2026-09"},
        "hypothetical_exposures": {"usd_liability": USD_LIABILITY, "usd_liability_unit": "USD", "cop_floating_rate_balance": COP_FLOATING_BALANCE, "cop_balance_unit": "COP", "assumption": "Constant outstanding principal, no hedges, taxes, amortization, accrued interest or cash-flow timing"},
        "formulas": {"fx_monthly_revaluation_cop": "USD 1,000,000 * (TRM_month_end_t - TRM_month_end_t-1)", "dtf_annualized_cost_change_cop": "COP 100,000,000,000 * (DTF_t - DTF_t-12) / 100; DTF changes are percentage points"},
        "aligned_window": {"start": frame.mes.min().strftime("%Y-%m"), "end": frame.mes.max().strftime("%Y-%m"), "months": len(frame)},
        "latest_aligned_observation": {"month": latest.mes.strftime("%Y-%m"), "trm_cop_usd": float(latest.trm_cop_usd), "hypothetical_usd_liability_cop": float(latest.fx_liability_cop), "fx_monthly_revaluation_cop_millions": None if pd.isna(latest.fx_revaluation_change_cop_millions) else float(latest.fx_revaluation_change_cop_millions), "dtf_percent_ea": float(latest.dtf_promedio), "dtf_12m_change_percentage_points": None if pd.isna(latest.delta_dtf_12m_pp) else float(latest.delta_dtf_12m_pp), "dtf_annualized_cost_change_cop_millions": None if pd.isna(latest.dtf_annualized_cost_change_cop_millions) else float(latest.dtf_annualized_cost_change_cop_millions)},
        "observed_sensitivity_range": {"fx_monthly_change_cop_millions_min": float(fx_active.fx_revaluation_change_cop_millions.min()), "fx_monthly_change_cop_millions_max": float(fx_active.fx_revaluation_change_cop_millions.max()), "dtf_12m_change_pp_min": float(dtf_active.delta_dtf_12m_pp.min()), "dtf_12m_change_pp_max": float(dtf_active.delta_dtf_12m_pp.max())},
        "ibr": "Not used: this application isolates a DTF-indexed hypothetical peso liability. IBR-based repricing requires a specified tenor, reset convention, spread, day count and a separately governed IBR vintage.",
        "limitations": ["TRM and DTF are public market reference series, not a company's realized FX or interest cash flows.", "The FX and DTF sensitivities are separate and must not be summed as a joint loss; no joint shock distribution or correlation model is estimated.", "Static principal, immediate pass-through and no hedge assumptions are illustrative. No entity exposure, hedge effectiveness, covenant breach or decision threshold is validated.", "The snapshot is a point-in-time extraction; source metadata may include observations dated after the local download date because of publication/time-zone timing. Use each observation date as published.", "The DTF raw SDMX source bytes are not preserved in this repository; lineage and derived-file hash are documented in the treasury-and-ALM README."]
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, constrained_layout=True)
    axes[0].plot(frame.mes, frame.fx_revaluation_change_cop_millions, color="#355C7D", lw=1.4)
    axes[0].axhline(0, color="#666", lw=.7)
    axes[0].set(title="Revaluación mensual de pasivo hipotético USD 1 millón", ylabel="COP millones")
    axes[1].plot(frame.mes, frame.dtf_annualized_cost_change_cop_millions, color="#C06C46", lw=1.4)
    axes[1].axhline(0, color="#666", lw=.7)
    axes[1].set(title="Cambio anualizado por DTF (saldo hipotético COP 100.000 millones)", ylabel="COP millones / año", xlabel="Mes")
    fig.suptitle("BanRep observado | sensibilidades separadas, principal constante", fontsize=14, weight="bold")
    fig.savefig(OUT / "market_factor_sensitivities.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"window": summary["aligned_window"], "latest": summary["latest_aligned_observation"], "sha256": {"trm": TRM_SHA256, "dtf": DTF_SHA256}}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
