"""Politicas de enrutamiento y su contabilidad (costo = suma de todos los niveles consultados)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .world import World


def _result(correct, cost, lat, nllamadas) -> dict:
    return {"correct": np.asarray(correct, float), "cost": np.asarray(cost, float), "latency": np.asarray(lat, float), "calls": np.asarray(nllamadas, float)}


def always_tier(df: pd.DataFrame, w: World, name: str) -> dict:
    n = len(df); t = next(x for x in w.tiers if x.name == name)
    return _result(df[f"correct_{name}"], np.full(n, t.cost_per_call), np.full(n, t.latency_ms), np.ones(n))


def cascade(df: pd.DataFrame, w: World, thresholds: list[float]) -> dict:
    """Cascada en el orden de `w.tiers`: se acepta la respuesta de un nivel si su confianza >= umbral; si no, se escala. El ultimo
    nivel siempre acepta. Costo y latencia acumulan TODOS los niveles consultados."""
    n = len(df); tiers = w.tiers; assert len(thresholds) == len(tiers) - 1
    vivo = np.ones(n, bool); correct = np.zeros(n); cost = np.zeros(n); lat = np.zeros(n); calls = np.zeros(n)
    for i, t in enumerate(tiers):
        cost[vivo] += t.cost_per_call; lat[vivo] += t.latency_ms; calls[vivo] += 1
        acepta = vivo & ((df[f"conf_{t.name}"].values >= thresholds[i]) if i < len(tiers) - 1 else True)
        correct[acepta] = df[f"correct_{t.name}"].values[acepta]; vivo = vivo & ~acepta
    return _result(correct, cost, lat, calls)


class LogisticReg:
    """Regresion logistica L2 en numpy (Newton-IRLS) para predecir el exito del nivel pequeno desde atributos observables."""
    def __init__(self, l2: float = 1.0, iters: int = 50): self.l2, self.iters = l2, iters

    def fit(self, X, y):
        X = np.column_stack([np.ones(len(X)), X]); w = np.zeros(X.shape[1]); R = self.l2 * np.eye(X.shape[1]); R[0, 0] = 0
        for _ in range(self.iters):
            p = 1 / (1 + np.exp(-X @ w)); g = X.T @ (p - y) + R @ w; H = X.T @ (X * (p * (1 - p))[:, None]) + R + 1e-9 * np.eye(X.shape[1]); step = np.linalg.solve(H, g); w -= step
            if np.abs(step).max() < 1e-9: break
        self.w = w; return self

    def predict_proba(self, X): return 1 / (1 + np.exp(-(np.column_stack([np.ones(len(X)), X]) @ self.w)))


FEATS = [f"f{j}" for j in range(5)]


def learned_router(train: pd.DataFrame, test: pd.DataFrame, w: World, tau: float, small: str = "small", big: str = "large") -> tuple[dict, np.ndarray]:
    """Enruta al nivel pequeno si la probabilidad predicha de que acierte es >= tau; si no, al grande. Sin segunda consulta."""
    m = LogisticReg().fit(train[FEATS].values, train[f"correct_{small}"].values); ph = m.predict_proba(test[FEATS].values); a_small = ph >= tau
    ts = next(t for t in w.tiers if t.name == small); tb = next(t for t in w.tiers if t.name == big)
    correct = np.where(a_small, test[f"correct_{small}"].values, test[f"correct_{big}"].values); cost = np.where(a_small, ts.cost_per_call, tb.cost_per_call); lat = np.where(a_small, ts.latency_ms, tb.latency_ms)
    return _result(correct, cost, lat, np.ones(len(test))), ph


def oracle_router(df: pd.DataFrame, w: World) -> dict:
    """Cota inferior de costo: elige el nivel mas barato que acierta; si ninguno acierta, el mas barato."""
    n = len(df); order = sorted(w.tiers, key=lambda t: t.cost_per_call); correct = np.zeros(n); cost = np.zeros(n); lat = np.zeros(n); hecho = np.zeros(n, bool)
    for t in order:
        ok = (df[f"correct_{t.name}"].values == 1) & ~hecho; correct[ok] = 1; cost[ok] = t.cost_per_call; lat[ok] = t.latency_ms; hecho |= ok
    t0 = order[0]; cost[~hecho] = t0.cost_per_call; lat[~hecho] = t0.latency_ms
    return _result(correct, cost, lat, np.ones(n))


def evaluate(res: dict) -> dict:
    return {"quality": float(res["correct"].mean()), "mean_cost": float(res["cost"].mean()), "mean_latency": float(res["latency"].mean()), "escalation_rate": float((res["calls"] > 1).mean())}


def pareto_frontier(points: list[tuple[float, float]]) -> list[int]:
    """Indices de los puntos (costo, calidad) no dominados: ninguno con costo <= y calidad >= y alguna desigualdad estricta."""
    idx = []
    for i, (c, q) in enumerate(points):
        dom = any((c2 <= c and q2 >= q) and (c2 < c or q2 > q) for j, (c2, q2) in enumerate(points) if j != i)
        if not dom: idx.append(i)
    return idx
