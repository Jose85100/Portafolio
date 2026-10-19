"""Reconcile versions by loan_id; never silently equate an old/new Stage3 route."""

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.baseline import CURRENT_SOURCE
from src.baseline import engine as historical


def load_current(path: Path = CURRENT_SOURCE) -> Any:
    spec = importlib.util.spec_from_file_location("ifrs9_current_reconciled", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load current IFRS9 source")
    module: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


current = load_current()


def reconciliation(portfolio: pd.DataFrame, eir: float = 0.1, horizon: int = 5) -> pd.DataFrame:
    """Base-scenario comparisons on the explicitly shared input domain.

    Changed caps/boundary semantics outside this domain are not silently claimed
    unchanged. The current engine validates its full portfolio contract first.
    """
    new = current.ecl_componentes(portfolio, "base", horizon, eir)
    if (portfolio.pd_12m >= 0.95).any() or (portfolio.lgd_base > 0.95).any():
        raise ValueError("shared comparison domain excludes changed legacy caps")
    if (portfolio.pd_origen < 1e-6).any():
        raise ValueError("shared comparison domain excludes changed origin-PD clipping")
    old = historical.ecl_componentes(portfolio, "base", horizon, eir)
    before = old[["loan_id", "stage", "ecl"]].rename(columns={"stage": "stage_old", "ecl": "ecl_old"})
    after = new[["loan_id", "stage", "ecl", "ecl_basis"]]
    table = before.merge(after, on="loan_id", how="outer", validate="one_to_one", indicator=True)
    if not table["_merge"].eq("both").all() or not table.stage.eq(table.stage_old).all():
        raise AssertionError("loan population or stage drift")
    table["difference"] = table.ecl - table.ecl_old
    table["relative_difference"] = table.difference / np.maximum(np.abs(table.ecl_old), 1e-300)
    return table.drop(columns="_merge")
