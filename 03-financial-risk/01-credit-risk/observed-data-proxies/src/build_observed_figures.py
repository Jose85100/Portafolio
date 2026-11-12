"""Build public-facing figures from the frozen observed ICETEX snapshot."""
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CURATED = DATA / "processed" / "delinquency_observed.csv"
RAW = DATA / "raw" / "icetex-dugh-vkir-2026-11-10.json"
OUT = ROOT / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

with CURATED.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
with RAW.open(encoding="utf-8") as stream:
    raw_rows = json.load(stream)

trend = defaultdict(lambda: {"total": 0, "over90": 0})
volume = defaultdict(int)
department = defaultdict(lambda: {"total": 0, "over90": 0})
latest = max(row["fecha_corte"] for row in rows)
for row in rows:
    cut, phase = row["fecha_corte"], row["epoca_cartera"]
    total, over90 = int(row["creditos_total"]), int(row["creditos_mora_mayor_90d"])
    trend[(cut, phase)]["total"] += total
    trend[(cut, phase)]["over90"] += over90
    volume[(cut, phase)] += total
    department[(cut, row["departamento"], phase)]["total"] += total
    department[(cut, row["departamento"], phase)]["over90"] += over90

phase_names = {"AMORTIZACION": "Amortización", "ESTUDIOS": "Estudios"}
colors = {"AMORTIZACION": "#155E75", "ESTUDIOS": "#D28E2B"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 12,
                     "axes.labelsize": 9, "figure.facecolor": "white", "axes.facecolor": "#F7F9FB"})

# 1. Credit-count-weighted stock share, never an average of department rates.
fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
for phase in ("AMORTIZACION", "ESTUDIOS"):
    dates = sorted(cut for cut, p in trend if p == phase)
    shares = [100 * trend[(cut, phase)]["over90"] / trend[(cut, phase)]["total"] for cut in dates]
    ax.plot(dates, shares, marker="o", markersize=3.5, linewidth=2, color=colors[phase],
            label=phase_names[phase])
ax.set(title="ICETEX: mora mayor a 90 días por etapa", ylabel="Créditos en mora >90 días / créditos reportados (%)",
       xlabel="Fecha de corte")
ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, ncol=2, loc="upper left")
ax.tick_params(axis="x", rotation=35)
fig.savefig(OUT / "icetex-90d-share-by-phase.png", dpi=180); plt.close(fig)

# 2. Reported credit counts by phase; counts are not balances or exposures.
fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
for phase in ("AMORTIZACION", "ESTUDIOS"):
    dates = sorted(cut for cut, p in volume if p == phase)
    counts = [volume[(cut, phase)] for cut in dates]
    ax.plot(dates, counts, marker="o", markersize=3.5, linewidth=2, color=colors[phase],
            label=phase_names[phase])
ax.set(title="ICETEX: créditos reportados por corte y etapa", ylabel="Suma de créditos en grupos departamento × etapa",
       xlabel="Fecha de corte")
ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, ncol=2, loc="upper left")
ax.tick_params(axis="x", rotation=35)
fig.savefig(OUT / "icetex-reported-credit-counts.png", dpi=180); plt.close(fig)

# 3. Latest-cut high-volume departments, with separate denominators by phase.
dept_totals = defaultdict(int)
for (cut, dept, phase), value in department.items():
    if cut == latest:
        dept_totals[dept] += value["total"]
top = [dept for dept, _ in sorted(dept_totals.items(), key=lambda item: (-item[1], item[0]))[:6]]
y = np.arange(len(top)); height = .34
fig, ax = plt.subplots(figsize=(10.2, 5.4), constrained_layout=True)
for offset, phase in ((-height/2, "AMORTIZACION"), (height/2, "ESTUDIOS")):
    shares, counts = [], []
    for dept in top:
        value = department[(latest, dept, phase)]
        shares.append(100 * value["over90"] / value["total"] if value["total"] else np.nan)
        counts.append(value["total"])
    bars = ax.barh(y + offset, shares, height, color=colors[phase], label=phase_names[phase])
    for bar, share, count in zip(bars, shares, counts):
        ax.annotate(f"{share:.1f}%  |  n={count:,}", (bar.get_width(), bar.get_y()+bar.get_height()/2),
                    xytext=(4, 0), textcoords="offset points", ha="left", va="center", fontsize=7)
ax.set(title=f"ICETEX: mora >90 días en los 6 departamentos con más créditos ({latest})",
       xlabel="Mora >90 días / créditos reportados (%)", ylabel="Departamento")
ax.set_yticks(y, top); ax.invert_yaxis(); ax.set_xlim(0, 40); ax.grid(axis="x", alpha=.25); ax.legend(frameon=False, ncol=2, loc="lower right")
fig.savefig(OUT / "icetex-department-comparison-latest.png", dpi=180); plt.close(fig)

# 4. Source quality: all failed count reconciliations are isolated in one cut.
invalid_by_cut = defaultdict(int)
valid_by_cut = defaultdict(int)
for row in raw_rows:
    cut = row["fecha_corte"][:10]
    try:
        current, short, over90, total = (int(row[key]) for key in (
            "cantidad_creditos_al_dia", "cantidad_creditos_con_mora",
            "cantidad_creditos_mora_mayor", "total_creditos"))
        if total == 0 or min(current, short, over90, total) < 0 or current + short + over90 != total:
            invalid_by_cut[cut] += 1
        else:
            valid_by_cut[cut] += 1
    except (ValueError, TypeError, KeyError):
        invalid_by_cut[cut] += 1
bad_cut = max(invalid_by_cut, key=invalid_by_cut.get)
other_valid = sum(count for cut, count in valid_by_cut.items() if cut != bad_cut)
other_invalid = sum(count for cut, count in invalid_by_cut.items() if cut != bad_cut)
labels = ["Otros cortes completos", bad_cut]
totals = [other_valid + other_invalid, valid_by_cut[bad_cut] + invalid_by_cut[bad_cut]]
fails = [other_invalid, invalid_by_cut[bad_cut]]
rates = [100 * fail / total if total else 0 for fail, total in zip(fails, totals)]
fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
bars = ax.bar(labels, rates, color=["#7A9E7E", "#B84A3A"], width=.55)
for bar, fail, total in zip(bars, fails, totals):
    ax.annotate(f"{fail} / {total} filas", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)
ax.set(title="Conciliación de conteos en la fuente ICETEX", ylabel="Filas que no concilian (%)", ylim=(0, max(rates+[5])*1.2))
ax.grid(axis="y", alpha=.25)
fig.savefig(OUT / "icetex-source-quality-by-cut.png", dpi=180); plt.close(fig)
