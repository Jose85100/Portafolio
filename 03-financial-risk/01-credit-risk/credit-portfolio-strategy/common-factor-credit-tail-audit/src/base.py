"""Load audited 25oct sibling without modifying or duplicating its numerical kernel."""

import importlib.util
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, cast


class TailValue(Protocol):
    var: float
    es: float


PATH = (
    Path(__file__).resolve().parents[2]
    / "discrete-credit-tail-audit"
    / "src"
    / "loss.py"
)
SPEC = importlib.util.spec_from_file_location("portfolio_discrete_credit_tail_25", PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"audited sibling kernel unavailable: {PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
independent_pmf = cast(
    Callable[[Sequence[int], Sequence[float]], list[float]], MODULE.independent_pmf
)
tail = cast(Callable[[Sequence[float], float], TailValue], MODULE.tail)
validate = cast(Callable[[Sequence[int], Sequence[float]], None], MODULE.validate)
