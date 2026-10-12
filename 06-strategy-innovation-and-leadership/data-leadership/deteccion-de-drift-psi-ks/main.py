import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

rng = np.random.default_rng(101)
n = 10000
ref = pd.DataFrame({
    "ingreso": rng.lognormal(8, 0.5, n),
    "edad": rng.normal(42, 11, n),
    "utilizacion": rng.beta(2, 3, n),
    "antiguedad": rng.exponential(5, n),
})
act = pd.DataFrame({
    "ingreso": rng.lognormal(8.15, 0.5, n),      # deriva moderada de nivel
    "edad": rng.normal(42, 11, n),                # estable
    "utilizacion": rng.beta(3.2, 3, n),           # deriva fuerte
    "antiguedad": rng.exponential(5.1, n),        # casi estable
})


def psi(e, a, bins=10):
    cortes = np.quantile(e, np.linspace(0, 1, bins + 1))
    cortes[0], cortes[-1] = -np.inf, np.inf
    pe = np.clip(np.histogram(e, cortes)[0] / len(e), 1e-4, None)
    pa = np.clip(np.histogram(a, cortes)[0] / len(a), 1e-4, None)
    return float(((pa - pe) * np.log(pa / pe)).sum())


filas = []
for col in ref.columns:
    p = psi(ref[col], act[col])
    ks = ks_2samp(ref[col], act[col])
    filas.append({"variable": col, "PSI": p, "KS": ks.statistic, "p_valor_KS": ks.pvalue,
                  "alerta": "ROJO" if p > 0.25 else "AMBAR" if p > 0.10 else "VERDE"})
tabla = pd.DataFrame(filas).set_index("variable")
print(tabla.round(4).to_string())
print("Variables a revisar:", list(tabla.index[tabla["alerta"] != "VERDE"]))
