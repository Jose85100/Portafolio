"""Monthly descriptive exchange-rate/inflation companion using DANE and BanRep snapshots."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "official"
FIG = ROOT / "reports" / "figures"
MONTHS = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5,
          "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9,
          "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
NS = {"g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}


def parse_trm(path: Path) -> tuple[dict[str, float], dict]:
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    series = root.find(".//g:Series", NS)
    if series is None:
        raise ValueError("BanRep XML does not contain a Series node")
    dimensions = {v.attrib.get("id"): v.attrib.get("value") for v in series.findall("g:SeriesKey/g:Value", NS)}
    if dimensions.get("REFERENCE_AREA") != "CO" or dimensions.get("UNIT_MEASURE") != "COP" or dimensions.get("FREQ") != "D":
        raise ValueError(f"Unexpected BanRep series dimensions: {dimensions}")
    daily = {}
    for obs in series.findall("g:Obs", NS):
        period = obs.find("g:ObsDimension", NS).attrib["value"]
        value = float(obs.find("g:ObsValue", NS).attrib["value"])
        if len(period) != 8 or not math.isfinite(value) or value <= 0 or period in daily:
            raise ValueError(f"Invalid/duplicate TRM observation {period}")
        daily[period] = value
    monthly: dict[str, list[float]] = defaultdict(list)
    for period, value in daily.items():
        monthly[f"{period[:4]}-{period[4:6]}"] .append(value)
    means = {period: float(np.mean(values)) for period, values in monthly.items()}
    meta = {"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
            "daily_observations": len(daily), "first_day": min(daily), "last_day": max(daily),
            "monthly_periods": len(means), "series_id": "DF_TRM_DAILY_HIST", "frequency": "D"}
    return means, meta


def parse_dane_ipc(path: Path) -> tuple[dict[str, float], dict]:
    raw = path.read_bytes()
    wb = load_workbook(path, data_only=True, read_only=True)
    if "IndicesIPC" not in wb.sheetnames:
        raise ValueError("DANE workbook lacks IndicesIPC sheet")
    rows = list(wb["IndicesIPC"].values)
    years = [int(x) for x in rows[8][1:25] if isinstance(x, (int, float))]
    indices = {}
    for row in rows[9:21]:
        month_name = row[0]
        if month_name not in MONTHS:
            raise ValueError(f"Unexpected DANE month label: {month_name}")
        for col, year in enumerate(years, start=1):
            value = row[col] if col < len(row) else None
            if value is None:
                continue
            value = float(value)
            period = f"{year:04d}-{MONTHS[month_name]:02d}"
            if not math.isfinite(value) or value <= 0 or period in indices:
                raise ValueError(f"Invalid/duplicate DANE IPC index {period}")
            indices[period] = value
    if len(indices) < 200:
        raise ValueError(f"Unexpectedly few DANE index observations: {len(indices)}")
    meta = {"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
            "monthly_observations": len(indices), "first_month": min(indices), "last_month": max(indices),
            "sheet": "IndicesIPC", "base": "December 2018 = 100", "vintage": "October 2026 release"}
    return indices, meta


def covariance_sum(fit, first: int, last: int) -> dict:
    cov = np.asarray(fit.cov_params())
    estimate = float(fit.params[first:last + 1].sum())
    variance = float(cov[first:last + 1, first:last + 1].sum())
    se = math.sqrt(max(0.0, variance))
    return {"estimate": estimate, "hac_se": se, "ci95_low": estimate - 1.96 * se,
            "ci95_high": estimate + 1.96 * se}


def main() -> dict:
    trm, trm_meta = parse_trm(RAW / "banrep-trm-daily-2003-2026-11-10.xml")
    ipc, ipc_meta = parse_dane_ipc(RAW / "dane-ipc-empalme-2003-oct2026.xlsx")
    periods = sorted(set(trm) & set(ipc))
    if periods != sorted(set(periods)) or len(periods) < 200:
        raise ValueError("Insufficient or invalid common monthly sample")
    expected = []
    year, month = map(int, periods[0].split("-"))
    end_year, end_month = map(int, periods[-1].split("-"))
    while (year, month) <= (end_year, end_month):
        expected.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    if periods != expected:
        raise ValueError("Common DANE/BanRep monthly data contain gaps")
    rows = []
    for i, period in enumerate(periods):
        year, month = map(int, period.split("-"))
        row = {"period": period, "year": year, "month": month,
               "ipc_index_dec2018_100": ipc[period], "trm_monthly_average_cop_per_usd": trm[period]}
        if i:
            row["cpi_monthly_inflation_log_pct"] = 100 * math.log(ipc[period] / ipc[periods[i - 1]])
            row["fx_devaluation_monthly_log_pct"] = 100 * math.log(trm[period] / trm[periods[i - 1]])
            rows.append(row)
    # Use contiguous months only; differences at the join are valid only if the period is adjacent.
    for row in rows:
        y, m = int(row["year"]), int(row["month"])
        previous = f"{y - 1:04d}-12" if m == 1 else f"{y:04d}-{m - 1:02d}"
        if previous not in ipc or previous not in trm:
            raise ValueError(f"Missing prior month for {row['period']}")
    # Build aligned lag model from the first month after differencing through the last month.
    by_period = {r["period"]: r for r in rows}
    model = []
    for row in rows:
        y, m = row["year"], row["month"]
        lag_periods = []
        for lag in range(1, 4):
            mm = m - lag
            yy = y
            while mm <= 0:
                mm += 12
                yy -= 1
            lag_periods.append(f"{yy:04d}-{mm:02d}")
        if all(p in by_period for p in lag_periods):
            r = dict(row)
            for lag, p in enumerate(lag_periods, 1):
                r[f"fx_devaluation_lag{lag}_log_pct"] = by_period[p]["fx_devaluation_monthly_log_pct"]
            r["trend_decades_since_2003"] = (12 * (y - 2003) + m - 1) / 120
            model.append(r)
    if len(model) < 150:
        raise ValueError("Too few monthly observations for distributed-lag model")
    y = np.array([r["cpi_monthly_inflation_log_pct"] for r in model])
    fxcols = [[r["fx_devaluation_monthly_log_pct"], r["fx_devaluation_lag1_log_pct"],
               r["fx_devaluation_lag2_log_pct"], r["fx_devaluation_lag3_log_pct"]] for r in model]
    time = np.array([r["trend_decades_since_2003"] for r in model])
    season = np.eye(12)[np.array([r["month"] - 1 for r in model])][:, 1:]
    x = sm.add_constant(np.column_stack([fxcols, time, season]), has_constant="add")
    fit = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    x_no_trend = sm.add_constant(np.column_stack([fxcols, season]), has_constant="add")
    fit_no_trend = sm.OLS(y, x_no_trend).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    names = ["intercept_pp", "current_devaluation", "lag1_devaluation", "lag2_devaluation",
             "lag3_devaluation", "linear_trend_per_decade"] + [f"month_{m:02d}" for m in range(2, 13)]
    coef = {name: {"estimate": float(fit.params[i]), "hac_se": float(fit.bse[i]),
                   "pvalue": float(fit.pvalues[i]), "ci95_low": float(fit.conf_int()[i, 0]),
                   "ci95_high": float(fit.conf_int()[i, 1])} for i, name in enumerate(names)}
    total_main = covariance_sum(fit, 1, 4)
    total_no_trend = covariance_sum(fit_no_trend, 1, 4)
    summary = {
        "data_source": "DANE monthly chained CPI index and Banco de la República daily TRM SDMX snapshot",
        "data_vintage": "DANE October 2026 release; BanRep SDMX extract prepared 2026-11-10",
        "source_files": [ipc_meta, trm_meta],
        "transformations": {"cpi": "100*log(IPC_t/IPC_(t-1)); DANE chained index, December 2018=100",
                            "fx": "100*log(monthly mean TRM_t/monthly mean TRM_(t-1)); COP per USD",
                            "monthly_mean": "arithmetic mean of daily official TRM observations within month"},
        "observations_in_regression": len(model), "regression_start": model[0]["period"],
        "regression_end": model[-1]["period"], "r_squared": float(fit.rsquared),
        "method": "OLS, Newey-West HAC maxlags=6; month-of-year fixed effects and linear time trend",
        "specification": "monthly CPI log change = current plus 3 lagged monthly log TRM changes + month effects + linear trend + error",
        "coefficients": coef, "four_month_sum_current_and_lags": total_main,
        "sensitivity_without_linear_trend": {"r_squared": float(fit_no_trend.rsquared),
                                               "four_month_sum_current_and_lags": total_no_trend},
        "interpretation": "conditional monthly association in a distributed-lag regression; not causal identification",
        "limitations": ["DANE chained index spans methodological base changes; the published series is an official link series, not a constant basket throughout the full sample",
                        "TRM is a reference rate, not an importer-specific transaction price; monthly averaging suppresses within-month timing",
                        "monthly regressions do not identify exogenous exchange-rate shocks; omitted costs, expectations, demand, administered prices and monetary responses remain",
                        "HAC standard errors address covariance dependence under assumptions, not endogeneity or structural breaks",
                        "current-vintage historical data do not reproduce the information set available to decision makers at each date"]}
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    for path, records in ((OUT / "monthly_panel.csv", rows), (OUT / "regression_sample.csv", model)):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    (OUT / "application_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 4.8))
        ax.plot([r["period"] for r in rows], [r["cpi_monthly_inflation_log_pct"] for r in rows], label="IPC mensual (log %) ", color="#b91c1c", lw=1)
        ax.plot([r["period"] for r in rows], [r["fx_devaluation_monthly_log_pct"] for r in rows], label="Devaluación TRM (log %) ", color="#245b72", lw=1, alpha=.8)
        ax.axhline(0, color="#64748b", lw=.7)
        ax.set(title="IPC y TRM: cambios mensuales observados en Colombia", ylabel="Cambio log mensual (%)", xlabel="Mes")
        tick_positions = list(range(0, len(rows), 24))
        ax.set_xticks(tick_positions, [rows[i]["period"] for i in tick_positions])
        ax.tick_params(axis="x", rotation=45)
        ax.legend(); fig.tight_layout(); fig.savefig(FIG / "dane-banrep-monthly-series.png", dpi=170); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6.5, 5.2))
        ax.scatter([r["fx_devaluation_monthly_log_pct"] for r in model], [r["cpi_monthly_inflation_log_pct"] for r in model], alpha=.5, s=18, color="#167c80")
        ax.set(title="Asociación mensual observada (sin identificación causal)", xlabel="Devaluación mensual TRM (%)", ylabel="Inflación IPC mensual (%)")
        fig.tight_layout(); fig.savefig(FIG / "dane-banrep-monthly-scatter.png", dpi=170); plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
