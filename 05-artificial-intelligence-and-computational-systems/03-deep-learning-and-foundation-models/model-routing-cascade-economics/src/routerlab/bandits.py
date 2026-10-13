"""Enrutamiento en linea como bandido de brazos multiples (un brazo por nivel); recompensa = acierto - lambda * costo normalizado."""
from __future__ import annotations
import numpy as np
from .world import World


def run_bandit(w: World, n: int, lam: float, algo: str, rng: np.random.Generator, eps: float = 0.1) -> dict:
    """Devuelve el arrepentimiento de pseudo-regret acumulado respecto del mejor brazo fijo (por esperanza verdadera)."""
    df = w.sample(n, rng); K = len(w.tiers); cmax = max(t.cost_per_call for t in w.tiers); names = [t.name for t in w.tiers]
    R = np.column_stack([df[f"correct_{t.name}"].values - lam * t.cost_per_call / cmax for t in w.tiers])                                    # recompensa observable de cada brazo (solo se ve la jalada)
    mu = np.array([df[f"p_{t.name}"].mean() - lam * t.cost_per_call / cmax for t in w.tiers]); best = mu.max()
    cnt = np.zeros(K); suma = np.zeros(K); alpha = np.ones(K); beta = np.ones(K); regret = np.zeros(n); elegidos = np.zeros(n, int)
    for t in range(n):
        if t < K: a = t
        elif algo == "eps_greedy": a = int(rng.integers(K)) if rng.random() < eps else int(np.argmax(suma / cnt))
        elif algo == "ucb": a = int(np.argmax(suma / cnt + (1 + lam) * np.sqrt(2 * np.log(t + 1) / cnt)))
        elif algo == "thompson": a = int(np.argmax(rng.beta(alpha, beta)))
        elif algo == "greedy": a = int(np.argmax(suma / cnt))
        else: raise ValueError(algo)
        r = R[t, a]; cnt[a] += 1; suma[a] += r; s = (r + lam) / (1 + lam); alpha[a] += float(rng.random() < s); beta[a] += float(rng.random() >= s)       # Thompson con recompensa en [0,1] (truco de Bernoulli)
        regret[t] = best - mu[a]; elegidos[t] = a
    return {"regret": np.cumsum(regret), "chosen": elegidos, "best_arm": names[int(np.argmax(mu))], "mu": mu}
