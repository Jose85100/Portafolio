"""Conciliacion entre fuente y destino y huella de contenido independiente del orden."""
from __future__ import annotations
import hashlib
import numpy as np
import pandas as pd


def content_hash(df: pd.DataFrame, decimals: int = 9) -> str:
    """SHA-256 sobre filas canonicas ordenadas: no depende del orden de filas ni de columnas; los flotantes se redondean a `decimals`."""
    cols = sorted(df.columns); canon = []
    for r in df[cols].itertuples(index=False):
        canon.append("|".join("" if (v is None or (isinstance(v, float) and np.isnan(v))) else (f"{v:.{decimals}f}" if isinstance(v, (float, np.floating)) else str(v)) for v in r))
    h = hashlib.sha256(); h.update(("|".join(cols) + "\n").encode())
    for line in sorted(canon): h.update((line + "\n").encode())
    return h.hexdigest()


def reconcile(source: pd.DataFrame, target: pd.DataFrame, key: str, numeric_cols: list[str]) -> dict:
    s, t = set(source[key]), set(target[key])
    out = {"rows_source": len(source), "rows_target": len(target), "row_diff": len(target) - len(source), "missing_in_target": sorted(s - t), "extra_in_target": sorted(t - s), "numeric": {}}
    for c in numeric_cols: out["numeric"][c] = {"sum_diff": float(target[c].sum() - source[c].sum()), "mean_diff": float(target[c].mean() - source[c].mean())}
    cols = sorted(set(source.columns) & set(target.columns)); out["hash_source"] = content_hash(source[cols]); out["hash_target"] = content_hash(target[cols]); out["equal"] = out["hash_source"] == out["hash_target"]
    return out
