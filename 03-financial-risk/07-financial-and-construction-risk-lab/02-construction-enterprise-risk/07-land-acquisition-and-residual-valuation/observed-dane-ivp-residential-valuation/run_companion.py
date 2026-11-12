#!/usr/bin/env python3
"""Build reproducible descriptive context from DANE IVP city results (2024–25)."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "city_variations_2024_2025.csv"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 22, f"Expected 22 DANE cities, got {len(rows)}"
assert len({r['city'] for r in rows}) == 22, "Duplicate city"
for r in rows:
    r['ivp_variation_2024_pct'] = float(r['ivp_variation_2024_pct'])
    r['ivp_variation_2025_pct'] = float(r['ivp_variation_2025_pct'])
    r['change_pp'] = round(r['ivp_variation_2025_pct'] - r['ivp_variation_2024_pct'], 2)

# Reconcile every transcribed cell to DANE's published table.
expected = {
 'Manizales': (3.53, 6.48), 'Pasto': (4.06, 5.97), 'Popayán': (3.59, 5.54),
 'Tunja': (4.62, 5.35), 'Armenia': (4.87, 5.19), 'Pereira': (2.90, 4.87),
 'Sincelejo': (3.33, 4.54), 'Valledupar': (3.96, 4.27), 'Montería': (3.59, 4.06),
 'Villavicencio': (3.59, 3.77), 'Florencia': (5.48, 3.06), 'Ibagué': (4.12, 3.04),
 'Santa Marta': (2.57, 2.96), 'Riohacha': (4.29, 2.96), 'Neiva': (4.89, 2.91),
 'Medellín': (3.22, 2.90), 'Cali': (3.76, 2.86), 'Barranquilla': (4.82, 2.79),
 'Bucaramanga': (5.57, 2.78), 'Cartagena': (3.38, 2.69), 'Cúcuta': (3.31, 2.56),
 'Quibdó': (2.17, 2.23),
}
assert {r['city']: (r['ivp_variation_2024_pct'], r['ivp_variation_2025_pct']) for r in rows} == expected, 'Transcription does not reconcile to the DANE table'
# DANE reports the national IVP separately; it is not the unweighted city mean.
with (OUT / "ivp_city_changes_2024_2025.csv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=['city','ivp_variation_2024_pct','ivp_variation_2025_pct','change_pp'])
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in w.fieldnames})

ordered = sorted(rows, key=lambda r: r['ivp_variation_2025_pct'])
fig, ax = plt.subplots(figsize=(9.5, 8.0))
colors = ['#bc4749' if r['change_pp'] < 0 else '#386641' for r in ordered]
ax.barh([r['city'] for r in ordered], [r['ivp_variation_2025_pct'] for r in ordered], color=colors)
ax.axvline(3.45, color='#1d3557', linestyle='--', linewidth=1.6, label='Nacional DANE: 3,45%')
ax.set_xlabel('Variación anual IVP, 2025 (%)')
ax.set_title('Valoración comercial de predios urbanos habitacionales por ciudad')
ax.legend(loc='lower right')
ax.grid(axis='x', alpha=.2)
fig.tight_layout()
fig.savefig(FIG / "ivp_city_variation_2025.png", dpi=170)
plt.close(fig)

source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
manifest = {
  "producer": "DANE",
  "indicator": "Índice de Valoración Predial (IVP), variación anual de predios urbanos de destino habitacional",
  "reference_periods": [2024, 2025],
  "geography": "22 cities; Bogotá is excluded from IVP coverage",
  "source_bulletin": "https://www.dane.gov.co/files/operaciones/IVP/bol-IVP-2025.pdf",
  "source_historical_series": "https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-valoracion-predial-ivp",
  "source_table": "DANE, Tabla 1. Variación anual del IVP total y según ciudades, 2024–2025",
  "transcription": "Values in city_variations_2024_2025.csv manually transcribed from the official bulletin table; output is reproducible from this versioned transcription.",
  "source_csv_sha256": source_hash,
  "observations": len(rows),
  "qa": {
    "unique_cities": len({r['city'] for r in rows}),
    "expected_city_count": 22,
    "min_2025_pct": min(r['ivp_variation_2025_pct'] for r in rows),
    "max_2025_pct": max(r['ivp_variation_2025_pct'] for r in rows),
    "national_2025_pct_reported_by_DANE": 3.45,
    "city_mean_is_not_used_as_national_estimate": True
  },
  "limits": ["Residential commercial appraisal movement, not vacant-land prices or transaction-level absorption.", "Not an appraisal of a specific parcel and not a validation sample for residual land valuation.", "DANE IVP excludes Bogotá and covers only 22 cities."]
}
(OUT / "source_quality_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest['qa'], ensure_ascii=False, indent=2))
