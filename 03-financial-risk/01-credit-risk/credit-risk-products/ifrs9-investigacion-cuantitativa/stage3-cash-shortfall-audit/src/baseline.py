"""Load and execute the actual parent IFRS9 engine unchanged."""

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

SOURCE = Path(__file__).resolve().parents[2] / "src" / "ifrs9_engine.py"
spec = importlib.util.spec_from_file_location("ifrs9_parent_baseline", SOURCE)
assert spec and spec.loader
engine: Any = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def legacy_ecl(
    gross: NDArray[np.float64], lgd_pv: NDArray[np.float64], pd12: float, horizon: int, eir: float
) -> NDArray[np.float64]:
    frame = pd.DataFrame(
        {
            "loan_id": np.arange(gross.size),
            "pd_12m": pd12,
            "pd_origen": pd12,
            "dpd": 95,
            "ead": gross,
            "lgd_base": lgd_pv,
            "ccf": 0.0,
            "undrawn": 0.0,
        }
    )
    out = engine.ecl_componentes(frame, "base", horizon, eir)
    assert out.stage.eq(3).all()
    return np.asarray(out.ecl, dtype=np.float64)
