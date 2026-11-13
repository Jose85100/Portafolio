"""Utilidades compartidas: carga de la capa de datos, logit y construcción de notebooks."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
PROC = RAIZ / "datos" / "procesados"


def cartera() -> pd.DataFrame:
    return pd.read_csv(PROC / "cartera_sfc_mensual.csv.gz")


def macro() -> pd.DataFrame:
    return pd.read_csv(PROC / "macro_mensual.csv").set_index("mes")


def tasas() -> pd.DataFrame:
    return pd.read_csv(PROC / "tasas_desembolsos_semanal.csv.gz", parse_dates=["semana"])


def usura() -> pd.DataFrame:
    return pd.read_csv(PROC / "usura_por_modalidad.csv", parse_dates=["desde", "hasta"])


def logit(p):
    """Logit que conserva el índice si recibe una Serie."""
    if isinstance(p, (pd.Series, pd.DataFrame)):
        return np.log(p / (1 - p))
    p = np.asarray(p, dtype=float)
    return np.log(p / (1 - p))


def expit(x):
    if isinstance(x, (pd.Series, pd.DataFrame)):
        return 1 / (1 + np.exp(-x))
    return 1 / (1 + np.exp(-np.asarray(x, dtype=float)))


def cop_billones(x: float) -> str:
    """Formato colombiano en billones de pesos (10^12)."""
    return f"{x / 1e12:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " billones"


def construir_notebook(celdas: list[tuple[str, str]], destino: Path, ejecutar: bool = True) -> None:
    """celdas: lista de (tipo, fuente) con tipo en {"md", "code"}. Ejecuta y guarda con salidas."""
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.cells = [nbformat.v4.new_markdown_cell(s) if t == "md" else nbformat.v4.new_code_cell(s) for t, s in celdas]
    if ejecutar:
        NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(destino.parent)}}).execute()
    nbformat.write(nb, destino)
