"""Asignacion de niveles bajo presupuesto: maximiza la suma de probabilidades de acierto con costo total acotado."""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog


def allocate(P: np.ndarray, costs: np.ndarray, budget: float) -> np.ndarray:
    """P[i, k]: prob. predicha de acierto de la consulta i en el nivel k. Relajacion de Lagrange: cada consulta elige argmax_k P[i,k] - lam*c_k;
    se busca por biseccion el menor lam con costo <= presupuesto y luego se gasta el remanente con las mejoras de mayor ganancia por costo.
    Devuelve el nivel elegido por consulta (entero)."""
    n, K = P.shape; costs = np.asarray(costs, float)
    def asigna(lam): return np.argmax(P - lam * costs[None, :], axis=1)
    cost = lambda a: costs[a].sum()
    if cost(np.full(n, int(np.argmax(costs)))) <= budget: return np.full(n, int(np.argmax(costs)))
    lo, hi = 0.0, 1e6
    for _ in range(100):
        mid = (lo + hi) / 2
        if cost(asigna(mid)) > budget: lo = mid
        else: hi = mid
    a = asigna(hi); gastado = cost(a)
    while True:
        mejor, mi, mk = 0.0, -1, -1
        for i in range(n):
            for k in range(K):
                dc = costs[k] - costs[a[i]]
                if dc > 0 and gastado + dc <= budget + 1e-12:
                    g = (P[i, k] - P[i, a[i]]) / dc
                    if g > mejor: mejor, mi, mk = g, i, k
        if mi < 0: break
        gastado += costs[mk] - costs[a[mi]]; a[mi] = mk
    return a


def value(P: np.ndarray, a: np.ndarray) -> float: return float(P[np.arange(len(a)), a].sum())


def lp_upper_bound(P: np.ndarray, costs: np.ndarray, budget: float) -> float:
    """Valor optimo de la relajacion lineal (x[i,k] en [0,1], sum_k x[i,k] = 1, costo total <= presupuesto): cota superior del entero."""
    n, K = P.shape; c = -P.ravel(); A_eq = np.zeros((n, n * K)); b_eq = np.ones(n)
    for i in range(n): A_eq[i, i * K:(i + 1) * K] = 1
    A_ub = np.tile(np.asarray(costs, float), n)[None, :]; r = linprog(c, A_ub=A_ub, b_ub=[budget], A_eq=A_eq, b_eq=b_eq, bounds=(0, 1), method="highs"); return float(-r.fun)
