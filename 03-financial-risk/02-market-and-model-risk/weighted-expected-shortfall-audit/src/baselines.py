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
    nodes: list[ast.stmt] = [
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(nodes) != 1:
        raise RuntimeError(f"baseline function {name} not found")
    module = ast.Module(body=nodes, type_ignores=[])
    namespace: dict[str, Any] = {
        "np": np,
        "mean": mean,
        "ceil": math.ceil,
        "TailRisk": lambda v, e, m: SimpleNamespace(var=v, es=e, mean=m),
    }
    exec(compile(module, relative, "exec"), namespace)
    return namespace[name]


HISTORICO = repo_function(
    "03-financial-risk/02-market-and-model-risk/var-es-tres-metodos/main.py", "historico"
)
CONSTRUCTION = repo_function(
    "03-financial-risk/07-financial-and-construction-risk-lab/python/src/risk_models.py", "empirical_var_es"
)


def historical_es(losses: ArrayLike, alpha: float) -> float:
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
