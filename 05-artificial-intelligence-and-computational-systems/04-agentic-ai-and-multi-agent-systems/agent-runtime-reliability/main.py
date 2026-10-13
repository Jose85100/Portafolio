"""Demostracion corta: falla metaestable por reintentos y como la contienen el presupuesto de reintentos y el cortacircuitos."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from agentrt.policies import RetryPolicy, RetryBudget, CircuitBreaker
from agentrt.sim import simulate_service

arr = np.full(300, 100); cap = np.r_[np.full(60, 150), np.full(20, 30), np.full(220, 150)]
casos = {"sin reintentos": (RetryPolicy(1), None, None), "n=5 jitter completo": (RetryPolicy(5, 0.5, 8.0, "full"), None, None),
         "n=5 + presupuesto 10%": (RetryPolicy(5, 0.5, 8.0, "full"), RetryBudget(0.1, 10.0), None), "n=5 + cortacircuitos": (RetryPolicy(5, 0.5, 8.0, "full"), None, CircuitBreaker(0.5, 20, 10, 5.0, 3))}
print(f"{'configuracion':26s} goodput  amplificacion  ok ultimos 50 s")
for n, (pol, bud, brk) in casos.items():
    r = simulate_service(arr, cap, 0.0, pol, np.random.default_rng(1), budget=bud, breaker=brk, collapse=2.0)
    print(f"{n:26s} {r['goodput']:.3f}    {r['amplification']:.2f}x          {r['ok'][250:300].mean() / 100:.0%}")
