import numpy as np
import pandas as pd
from scipy.optimize import minimize

activos = ["acciones_local", "acciones_global", "bonos_gob", "bonos_corp", "commodities"]
mu = np.array([0.095, 0.085, 0.060, 0.070, 0.050])
vol = np.array([0.20, 0.16, 0.07, 0.09, 0.22])
corr = np.array([
    [1.00, 0.70, 0.10, 0.30, 0.40],
    [0.70, 1.00, 0.05, 0.35, 0.35],
    [0.10, 0.05, 1.00, 0.65, -0.05],
    [0.30, 0.35, 0.65, 1.00, 0.15],
    [0.40, 0.35, -0.05, 0.15, 1.00],
])
cov = np.outer(vol, vol) * corr
rf, n = 0.03, len(mu)
cons_suma = {"type": "eq", "fun": lambda w: w.sum() - 1}
limites = [(0, 1)] * n
w0 = np.full(n, 1 / n)


def minima_varianza(objetivo=None):
    cons = [cons_suma]
    if objetivo is not None:
        cons.append({"type": "eq", "fun": lambda w: w @ mu - objetivo})
    return minimize(lambda w: w @ cov @ w, w0, bounds=limites, constraints=cons, method="SLSQP").x


gmv = minima_varianza()
sharpe = minimize(lambda w: -(w @ mu - rf) / np.sqrt(w @ cov @ w), w0, bounds=limites,
                  constraints=[cons_suma], method="SLSQP").x

print("Frontera eficiente (retorno objetivo -> volatilidad):")
for obj in np.linspace(gmv @ mu, mu.max() * 0.97, 6):
    w = minima_varianza(obj)
    print(f"  retorno {w @ mu:.3%} | volatilidad {np.sqrt(w @ cov @ w):.3%}")

tabla = pd.DataFrame({"min_varianza": gmv, "max_sharpe": sharpe}, index=activos)
print(tabla.round(3).to_string())
for nombre, w in (("min_varianza", gmv), ("max_sharpe", sharpe)):
    r, s = w @ mu, np.sqrt(w @ cov @ w)
    print(f"{nombre}: retorno {r:.3%} | vol {s:.3%} | Sharpe {(r - rf) / s:.3f}")
