#!/usr/bin/env python3
"""Observed sign-regime diagnostic from DANE's annual ISE growth series."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
EXPECTED_SHA256 = "4e333c97b6558eb7e1b82d17fb8a0aa966f9113c87f099fa000f2390a3d7a199"
EXPECTED_BYTES = 487882
SOURCE_ID = "1y85mYZ4aPD4IorJx53M8XR69JM1GrzRn"
SOURCE_PAGE = "https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/indicador-de-seguimiento-a-la-economia-ise"
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract(path: Path) -> tuple[list[dict], dict]:
    if not path.is_file():
        raise FileNotFoundError(f"No existe el XLSX indicado en --ise-source: {path}")
    digest = sha256(path)
    if digest != EXPECTED_SHA256 or path.stat().st_size != EXPECTED_BYTES:
        raise ValueError(f"La fuente no coincide con el vintage registrado: bytes={path.stat().st_size}, sha256={digest}")

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["Cuadro 1"]
    rows = {i: tuple(row) for i, row in enumerate(ws.iter_rows(min_row=11, max_row=57, values_only=True), 11)}
    years_row, months_row, data_row = rows[42], rows[43], rows[57]
    if years_row[13] != 2006 or years_row[25] != 2007 or data_row[0] != "Indicador de Seguimiento a la Economía":
        raise ValueError("No coincide el esquema esperado del Cuadro 1 del ISE DANE")

    observations: list[dict] = []
    for col in range(14, 261):  # Excel columns N:IZ: Jan-2006 through Jul-2026.
        year = 2006 + (col - 14) // 12
        month = (col - 14) % 12 + 1
        value = data_row[col - 1]
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"ISE anual ausente/no numérico para {year}-{month:02d}")
        label = "crecimiento negativo" if value < 0 else "crecimiento no negativo"
        observations.append({
            "date": f"{year}-{month:02d}",
            "year": year,
            "month": month,
            "ise_yoy_growth_pct": float(value),
            "state": label,
            "period_status": "preliminar/provisional" if year >= 2024 else "según vintage DANE",
        })
    wb.close()
    if len(observations) != 247 or observations[0]["date"] != "2006-01" or observations[-1]["date"] != "2026-07":
        raise ValueError("La cobertura temporal del ISE difiere de enero de 2006–julio de 2026")

    metadata = {
        "source": "DANE, Indicador de Seguimiento a la Economía (ISE), Cuadro 1, serie original, tasas de crecimiento anuales",
        "source_page": SOURCE_PAGE,
        "drive_file_id": SOURCE_ID,
        "atlas_manifest_vintage": "2026-10-08",
        "source_snapshot_modified": "2026-10-08T17:13:03.954Z",
        "source_file": path.name,
        "source_path_policy": "Ruta de entrada --ise-source; la ruta local no se persiste",
        "source_bytes": path.stat().st_size,
        "source_sha256": digest,
        "workbook_sheet": "Cuadro 1",
        "workbook_row": "Indicador de Seguimiento a la Economía, fila de tasas de crecimiento anuales",
        "source_grain": "Colombia × mes",
        "source_period": "2006-01 to 2026-07; ending observation is 2026pr",
        "observation_unit": "percent year over year",
        "derived_state_rule": "negative if ISE annual growth < 0%; nonnegative otherwise",
        "n_observations": len(observations),
    }
    return observations, metadata


def spell_summary(states: list[int]) -> dict[int, dict]:
    spells = []
    start = 0
    for i in range(1, len(states)):
        if states[i] != states[i - 1]:
            spells.append((states[i - 1], i - start, i == len(states) - 1))
            start = i
    spells.append((states[-1], len(states) - start, True))
    summary = {}
    for state in (0, 1):
        durations = [length for s, length, _ in spells if s == state]
        completed = [length for s, length, censored in spells if s == state and not censored]
        summary[state] = {
            "episodes": len(durations),
            "mean_duration_months_all_including_right_censored": float(np.mean(durations)),
            "max_duration_months": int(max(durations)),
            "completed_episodes": len(completed),
        }
    return summary


def write_outputs(obs: list[dict], metadata: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "manifest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    table = REPORT_DIR / "ise_sign_regimes_monthly.csv"
    with table.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(obs[0]))
        writer.writeheader()
        writer.writerows(obs)

    binary = [0 if row["ise_yoy_growth_pct"] < 0 else 1 for row in obs]
    counts = np.zeros((2, 2), dtype=int)
    for a, b in zip(binary[:-1], binary[1:]):
        counts[a, b] += 1
    probs = counts / counts.sum(axis=1, keepdims=True)
    periods = [date.fromisoformat(row["date"] + "-01") for row in obs]
    growth = np.array([row["ise_yoy_growth_pct"] for row in obs])
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.3), gridspec_kw={"height_ratios": [2.1, 1]}, constrained_layout=True)
    ax = axes[0]
    ax.plot(periods, growth, color="#175D73", linewidth=1.45)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.fill_between(periods, growth, 0, where=(growth < 0), color="#C46B37", alpha=0.48, interpolate=True, label="crecimiento ISE interanual < 0")
    ax.set_title("ISE: crecimiento interanual y episodios de signo negativo", loc="left", fontsize=12, weight="bold")
    ax.set_ylabel("Variación anual (%)")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, loc="upper left")

    im = axes[1].imshow(probs, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    axes[1].set_xticks([0, 1], labels=["negativo", "no negativo"])
    axes[1].set_yticks([0, 1], labels=["negativo", "no negativo"])
    axes[1].set_xlabel("Estado en el mes siguiente")
    axes[1].set_ylabel("Estado en el mes actual")
    axes[1].set_title("Transición empírica de signo (probabilidades por fila)", loc="left", fontsize=11, weight="bold")
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, f"{probs[i,j]:.1%}\n(n={counts[i,j]})", ha="center", va="center", color="black")
    fig.colorbar(im, ax=axes[1], fraction=0.026, pad=0.02, label="Probabilidad")
    fig.suptitle("Régimen observado por signo del crecimiento del ISE · DANE", fontsize=14, weight="bold")
    fig.savefig(REPORT_DIR / "figures" / "ise_sign_regimes.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    n_negative = sum(s == 0 for s in binary)
    spell = spell_summary(binary)
    p_nn, p_pp = probs[0, 0], probs[1, 1]
    start, end = obs[0]["date"], obs[-1]["date"]
    latest = obs[-1]
    report = f"""# Aplicación observada: regímenes de signo del ISE

## Resultado

En la muestra {start}–{end} hay {len(obs)} observaciones mensuales. La tasa anual del ISE fue negativa en {n_negative} meses ({n_negative/len(obs):.1%}). Bajo la regla binaria de este companion, la probabilidad empírica de permanecer en crecimiento negativo al mes siguiente es {p_nn:.1%} (n={counts[0,0]} transiciones); la de permanecer en crecimiento no negativo es {p_pp:.1%} (n={counts[1,1]}). El último dato es {latest['ise_yoy_growth_pct']:.2f}% en {latest['date']} y corresponde a período preliminar.

El estado negativo aparece en {spell[0]['episodes']} episodios, todos completados dentro de la muestra, de duración media {spell[0]['mean_duration_months_all_including_right_censored']:.2f} meses y máximo de {spell[0]['max_duration_months']} meses. El spell final de crecimiento no negativo está censurado a la derecha en julio de 2026; no se usa como duración completa.

![Serie y transición empírica](figures/ise_sign_regimes.png)

## Definición y método

Se toma directamente la fila de crecimiento anual del total ISE en la serie original del Cuadro 1 DANE. El estado es “crecimiento negativo” si la variación interanual reportada es menor que cero y “crecimiento no negativo” en caso contrario. Se cuentan transiciones mensuales consecutivas y se normalizan por el estado de origen. La clasificación es transparente y no ajusta un modelo oculto de Markov.

Este proxy mide el signo del crecimiento anual de un indicador sintético de actividad mensual. No equivale a una fecha oficial de recesión, a una brecha del producto ni al crecimiento mensual del PIB. El ISE resume cambios de corto plazo y puede ser revisado; los meses 2024p–2026pr se conservan con su estado preliminar/provisional en el CSV.

## Fuente, vintage y reproducción

Fuente primaria: [DANE, Indicador de Seguimiento a la Economía](​{SOURCE_PAGE}); anexo “dane_ise_jul2026.xlsx”, actualizado por DANE el 18-sep-2026. El Atlas registra el crudo en su manifiesto de integridad con vintage 2026-10-08. El SHA-256 esperado es `{metadata['source_sha256']}` ({metadata['source_bytes']} bytes). El archivo canónico no se duplica en este producto: el runner recibe su ruta de entrada y no persiste la ruta local.

```bash
python3 -m pip install openpyxl numpy matplotlib
python3 observed_application.py --ise-source "/ruta/a/Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/dane_ise_jul2026.xlsx"
```

El runner verifica nombre de hoja/fila, fecha inicial/final, completitud, tamaño y hash antes de escribir. Salidas: `reports/ise_sign_regimes_monthly.csv`, `reports/figures/ise_sign_regimes.png` y `data/manifest.json`.

## Interpretación y alcance

La fuerte persistencia del signo no negativo describe el saldo de los regímenes observados y ayuda a localizar episodios para un análisis posterior. No identifica el origen de las transiciones ni una respuesta causal a la tasa de política. El resultado depende del umbral cero, de la agregación anual-interanual y de la composición del ISE; una especificación Markov-switching requeriría estimar estados latentes, comparar distribuciones condicionales, contrastar cantidad de estados y tratar revisiones/vintages.

El laboratorio sintético permanece intacto y sigue sirviendo para probar estimadores de cambio de régimen con DGP controlado. Esta aplicación observada evalúa el comportamiento del proxy en datos DANE; no demuestra la validez de un modelo oculto de Markov ni su desempeño de pronóstico.
""".replace("\u200b", "")
    (REPORT_DIR / "observed_application.md").write_text(report, encoding="utf-8")
    transition_path = REPORT_DIR / "ise_transition_matrix.csv"
    with transition_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["from_state", "to_state", "count", "row_probability"])
        for i, a in enumerate(("negative", "nonnegative")):
            for j, b in enumerate(("negative", "nonnegative")):
                writer.writerow([a, b, int(counts[i, j]), float(probs[i, j])])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ise-source", required=True, type=Path, help="Ruta al XLSX DANE canónico en 01_RAW")
    args = parser.parse_args()
    observations, manifest = extract(args.ise_source.expanduser())
    write_outputs(observations, manifest)
    states = [0 if row["ise_yoy_growth_pct"] < 0 else 1 for row in observations]
    counts = np.zeros((2, 2), dtype=int)
    for a, b in zip(states[:-1], states[1:]):
        counts[a, b] += 1
    probs = counts / counts.sum(axis=1, keepdims=True)
    print(f"n={len(observations)}; sha256={manifest['source_sha256']}; end={observations[-1]['date']}")
    print(f"negative_months={sum(s == 0 for s in states)}; P(neg->neg)={probs[0,0]:.4%}; P(nonneg->nonneg)={probs[1,1]:.4%}")
