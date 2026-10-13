"""Bucle de agente guionado (sin LLM) protegido por presupuesto y detector de bucles."""
from __future__ import annotations
import numpy as np
from .policies import BudgetGuard, BudgetExceeded, LoopDetector


def run_agent(policy_fn, tool_fn, guard: BudgetGuard | None, loop: LoopDetector | None, max_hard: int = 10_000) -> dict:
    """policy_fn(historial) -> accion (tool, args) o None para terminar. tool_fn(tool, args) -> (resultado, costo).
    max_hard evita bucles infinitos reales en la simulacion. Devuelve pasos, costo y motivo de parada."""
    hist = []; cost = 0.0
    for step in range(max_hard):
        act = policy_fn(hist)
        if act is None: return {"stop": "done", "steps": step, "cost": cost}
        tool, args = act
        if loop is not None and loop.observe(tool, args): return {"stop": "loop_detected", "steps": step, "cost": cost}
        res, c = tool_fn(tool, args); cost += c; hist.append((tool, args, res))
        if guard is not None:
            try: guard.charge(cost=c)
            except BudgetExceeded as e: return {"stop": f"budget:{e}", "steps": step + 1, "cost": cost}
    return {"stop": "hard_limit", "steps": max_hard, "cost": cost}
