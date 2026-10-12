import numpy as np
import pandas as pd
from scipy.optimize import minimize

activos = ["acciones", "bonos_largos", "bonos_corp", "oro", "inmobiliario"]
vol = np.array([0.18, 0.08, 0.10, 0.15, 0.17])
corr = np.array([
    [1.00, -0.20, 0.35, 0.05, 0.60],
    [-0.20, 1.00, 0.55, 0.10, 0.05],
    [0.35, 0.55, 1.00, 0.10, 0.30],
    [0.05, 0.10, 0.10, 1.00, 0.10],
    [0.60, 0.05, 0.30, 0.10, 1.00],
])
cov = np.outer(vol, vol) * corr
n = len(vol)


def contribuciones(w):
    riesgo = np.sqrt(w @ cov @ w)
    return w * (cov @ w) / riesgo, riesgo


def objetivo(w):
    rc, _ = contribuciones(w)
    return ((rc - rc.mean()) ** 2).sum() * 1e4


cons = {"type": "eq", "fun": lambda w: w.sum() - 1}
rp = minimize(objetivo, np.full(n, 1 / n), bounds=[(0.001, 1)] * n, constraints=[cons],
              method="SLSQP", options={"ftol": 1e-14, "maxiter": 500}).x
mv = minimize(lambda w: w @ cov @ w, np.full(n, 1 / n), bounds=[(0, 1)] * n, constraints=[cons],
              method="SLSQP").x
ew = np.full(n, 1 / n)

for nombre, w in (("pesos_iguales", ew), ("min_varianza", mv), ("paridad_riesgo", rp)):
    rc, riesgo = contribuciones(w)
    print(f"{nombre}: volatilidad {riesgo:.3%}")
    print("  pesos:", dict(zip(activos, w.round(3).tolist())))
    print("  % del riesgo:", dict(zip(activos, (rc / riesgo).round(3).tolist())))
