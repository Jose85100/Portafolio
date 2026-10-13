"""Sagas: secuencia de pasos con compensaciones para lograr todo-o-nada sin transacciones distribuidas."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from .sim import Ledger


@dataclass
class Step:
    name: str
    p_fail: float = 0.0           # prob. de que la accion falle (sin efecto)
    p_comp_fail: float = 0.0      # prob. de que cada intento de compensacion falle


def run_saga(steps: list[Step], ledger: Ledger, rng: np.random.Generator, comp_retries: int = 5) -> dict:
    """Ejecuta los pasos en orden; si uno falla, compensa en orden inverso los ya aplicados (con reintentos).

    Los efectos se registran en el libro: accion aplica ('do', i); compensacion aplica ('undo', i).
    Resultado: 'committed' (todos), 'compensated' (ninguno neto), 'stuck' (alguna compensacion agoto reintentos).
    Invariante verificable: estado neto del paso i = #do - #undo en {0,1}; committed => todos 1; compensated => todos 0.
    """
    done: list[int] = []
    for i, s in enumerate(steps):
        if rng.random() < s.p_fail: break
        ledger.apply(("do", i)); done.append(i)
    else:
        return {"status": "committed", "applied": len(done)}
    stuck = False
    for i in reversed(done):
        for _ in range(comp_retries):
            if rng.random() >= steps[i].p_comp_fail: ledger.apply(("undo", i)); break
        else: stuck = True
    return {"status": "stuck" if stuck else "compensated", "applied": len(done)}


def net_state(ledger: Ledger, n_steps: int) -> list[int]:
    return [ledger.applied.get(("do", i), 0) - ledger.applied.get(("undo", i), 0) for i in range(n_steps)]
