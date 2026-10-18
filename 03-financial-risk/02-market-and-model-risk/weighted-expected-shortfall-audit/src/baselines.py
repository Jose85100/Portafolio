"""Execute the repository's actual baseline function bodies without demo side effects."""

import ast
import math
from pathlib import Path
from statistics import mean
from types import SimpleNamespace
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

ROOT = Path(__file__).resolve().parents[4]


def repo_function(relative: str, name: str) -> Any:
    source = (ROOT / relative).read_text()
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    if name not in functions:
        raise RuntimeError(f"baseline function {name} not found")
    # Include sibling helper definitions referenced by the selected body, while
    # excluding top-level demos, RNG draws and other import-time side effects.
    selected = {name}
    pending = [name]
    while pending:
        current = pending.pop()
        for node in ast.walk(functions[current]):
            if isinstance(node, ast.Name) and node.id in functions and node.id not in selected:
                selected.add(node.id)
                pending.append(node.id)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in selected]
    module = ast.Module(body=nodes, type_ignores=[])
    namespace: dict[str, Any] = {
        "np": np,
        "mean": mean,
        "ceil": math.ceil,
        "fsum": math.fsum,
        "isfinite": math.isfinite,
        "TailRisk": lambda v, e, m: SimpleNamespace(var=v, es=e, mean=m),
    }
    exec(compile(module, relative, "exec"), namespace)
    return namespace[name]


HISTORICO = repo_function(
    "03-financial-risk/02-market-and-model-risk/var-es-tres-metodos/main.py", "historico_legacy_conditional"
)
CONSTRUCTION = repo_function(
    "03-financial-risk/07-financial-and-construction-risk-lab/python/src/risk_models.py", "empirical_var_es"
)


def historical_es(losses: ArrayLike, alpha: float) -> float:
    """Named legacy comparator; not the default current historical ES API."""
    return float(HISTORICO(-np.asarray(losses, dtype=float), alpha)[1])


def construction_es(losses: ArrayLike, alpha: float) -> float:
    return float(CONSTRUCTION(np.asarray(losses, dtype=float).tolist(), alpha)["es"])


def strict_tail_es(losses: ArrayLike, alpha: float) -> float:
    """Ablation: discard the quantile atom. NaN if the strict tail is empty."""
    x = np.asarray(losses, dtype=float)
    tail = x[x > np.quantile(x, alpha, method="inverted_cdf")]
    return float(tail.mean()) if len(tail) else float("nan")


LIQUIDITY = repo_function("03-financial-risk/03-market-liquidity-research/python/laboratorio.py", "tail_risk")


def liquidity_es(losses: ArrayLike, alpha: float) -> float:
    return float(LIQUIDITY(losses, alpha).es)


HISTORICAL_CORRECTED = repo_function(
    "03-financial-risk/02-market-and-model-risk/var-es-tres-metodos/main.py", "historico"
)

def historical_corrected_es(losses: ArrayLike, alpha: float) -> float:
    return float(HISTORICAL_CORRECTED(-np.asarray(losses,dtype=float),alpha)[1])
