"""Load actual repository comparators without changing their behavior."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[4]
LEGACY_PATH = (
    ROOT / "03-financial-risk/02-market-and-model-risk/weighted-expected-shortfall-audit/src/tail.py"
)
ORACLE_PATH = ROOT / "04-quant-strategy-and-products/risk-engines/weighted-tail-audit/benchmarks/audit.py"
SHARED_FIXTURES = (
    ROOT / "04-quant-strategy-and-products/risk-engines/weighted-tail-audit/results/fixtures.json"
)


def load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


legacy = load(LEGACY_PATH, "underflow_legacy_tail")
oracle = load(ORACLE_PATH, "underflow_hinge_oracle")
