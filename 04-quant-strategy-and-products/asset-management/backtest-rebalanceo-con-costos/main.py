import numpy as np
import pandas as pd
from scipy.optimize import minimize

rng = np.random.default_rng(41)
n_act, dias = 5, 2520
vol = np.array([0.18, 0.15, 0.08, 0.10, 0.20]) / np.sqrt(252)
mu = np.array([0.08, 0.07, 0.04, 0.05, 0.06]) / 252
A = rng.uniform(-0.2, 0.6, (n_act, n_act))
corr = A @ A.T
d = np.sqrt(np.diag(corr))
corr = corr / np.outer(d, d)
L = np.linalg.cholesky(np.outer(vol, vol) * corr)
r = mu + rng.standard_normal((dias, n_act)) @ L.T
costo_bp, ventana, paso = 10, 252, 21


def min_var(cov):
    n = cov.shape[0]
    return minimize(lambda w: w @ cov @ w, np.full(n, 1 / n), bounds=[(0, 1)] * n,
                    constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}], method="SLSQP").x


def correr(estrategia):
    w_obj = np.full(n_act, 1 / n_act)
    w = w_obj.copy()
    retornos, rotacion = [], 0.0
    for t in range(ventana, dias):
        if (t - ventana) % paso == 0:
            w_obj = np.full(n_act, 1 / n_act) if estrategia == "iguales" else min_var(np.cov(r[t - ventana:t].T))
            rot = np.abs(w_obj - w).sum()
            rotacion += rot
            costo = rot * costo_bp / 1e4
            w = w_obj
        else:
            costo = 0.0
        bruto = w @ r[t]
        retornos.append(bruto - costo)
        w = w * (1 + r[t])
        w = w / w.sum()
    return np.array(retornos), rotacion


print(f"{'estrategia':>12} {'retorno_anual':>14} {'vol_anual':>10} {'Sharpe':>7} {'rotacion_total':>15}")
for est in ("iguales", "min_varianza"):
    ret, rot = correr(est)
    anual = ret.mean() * 252
    vola = ret.std(ddof=1) * np.sqrt(252)
    print(f"{est:>12} {anual:>14.2%} {vola:>10.2%} {anual / vola:>7.2f} {rot:>15.2f}")
