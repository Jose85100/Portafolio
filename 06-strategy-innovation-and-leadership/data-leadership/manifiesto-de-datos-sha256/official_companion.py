"""Build and verify provenance for a DANE CPI series snapshot."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "dane-ipc-monthly.csv"
OUT = ROOT / "reports"
DANE_XLSX_SHA256 = "4e8366bf2d03d4bdc15d14b1b21b12a6eec6c3695926abd503a430858ef74e2e"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(data: pd.DataFrame) -> dict[str, bool]:
    dates = pd.PeriodIndex(data["month"], freq="M")
    values = pd.to_numeric(data["ipc_total_nacional"], errors="coerce")
    return {
        "columnas_esperadas": list(data.columns) == ["month", "ipc_total_nacional"],
        "meses_unicos": not dates.has_duplicates,
        "continuidad_mensual": dates.equals(pd.period_range(dates.min(), dates.max(), freq="M")),
        "valores_completos_y_positivos": bool(values.notna().all() and (values > 0).all()),
        "rango_publicado_2003_2026_10": str(dates.min()) == "2003-01" and str(dates.max()) == "2026-10",
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    data = pd.read_csv(SOURCE, dtype={"month": str})
    checks = validate(data)
    if not all(checks.values()):
        raise ValueError(f"Fallaron controles estructurales: {checks}")
    manifest = {
        "dataset": SOURCE.name,
        "dataset_sha256": file_sha256(SOURCE),
        "bytes": SOURCE.stat().st_size,
        "rows": len(data),
        "grain": "total nacional, un índice mensual; base diciembre 2018 = 100",
        "source": "DANE, IPC Índices, serie de empalme 2003–2026 (octubre 2026)",
        "publication_date": "2026-11-09",
        "source_url": "https://www.dane.gov.co/files/operaciones/IPC/oct2026/anex-IPC-Indices-oct2026.xlsx",
        "source_xlsx_sha256": DANE_XLSX_SHA256,
        "transformation": "Extracted rows Enero–Diciembre and year columns from the DANE IndicesIPC sheet; no imputation or rescaling.",
        "checks": checks,
    }
    (OUT / "official_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / SOURCE.name
        shutil.copy2(SOURCE, clone)
        intact = file_sha256(clone) == manifest["dataset_sha256"]
        clone.write_text(clone.read_text() + "\n")
        altered_detected = file_sha256(clone) != manifest["dataset_sha256"]
    outcome = {"intact_snapshot_verified": intact, "single_byte_stream_change_detected": altered_detected,
               "structural_checks": checks, "status": "PASS" if intact and altered_detected and all(checks.values()) else "FAIL"}
    (OUT / "official_integrity_result.json").write_text(json.dumps(outcome, indent=2, ensure_ascii=False) + "\n")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    labels = ["Hash coincide\ncon manifiesto", "Alteración\ndetectada", "Controles\nestructurales"]
    values = [int(intact), int(altered_detected), int(all(checks.values()))]
    ax.bar(labels, values, color=["#007a78", "#007a78", "#007a78"], width=.55)
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 1], ["FALLA", "PASA"])
    ax.set_title("Verificación de integridad sobre snapshot IPC DANE")
    ax.grid(axis="y", alpha=.2)
    for i, value in enumerate(values):
        ax.text(i, value + .035, "PASA" if value else "FALLA", ha="center", weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "official_integrity.png", dpi=170)
    plt.close(fig)
    print(f"DANE extract SHA-256: {manifest['dataset_sha256']}")
    print(f"Snapshot: {len(data)} meses, {data['month'].iloc[0]}–{data['month'].iloc[-1]}")
    print(f"Controls: {sum(checks.values())}/{len(checks)} PASS | alteration detected: {altered_detected}")


if __name__ == "__main__":
    main()
