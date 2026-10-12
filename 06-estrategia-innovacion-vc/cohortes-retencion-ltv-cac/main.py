import numpy as np
import pandas as pd

rng = np.random.default_rng(79)
cohortes, tam, meses = 8, 1000, 12
arpu, margen, cac = 40.0, 0.78, 260.0
churn_base = np.array([0.12, 0.08, 0.06, 0.05, 0.045, 0.04, 0.04, 0.04, 0.035, 0.035, 0.035, 0.035])

filas = {}
for c in range(cohortes):
    factor = 1.0 + (0.7 if c == 5 else 0.0) + rng.normal(0, 0.05)
    activos = tam
    ret = []
    for m in range(meses):
        activos = rng.binomial(activos, 1 - min(churn_base[m] * factor, 0.99))
        ret.append(activos / tam)
    filas[f"C{c + 1}"] = ret

ret = pd.DataFrame(filas, index=range(1, meses + 1)).T
print("Retencion por cohorte (meses 1, 3, 6, 12):")
print(ret[[1, 3, 6, 12]].round(3).to_string())

churn_mensual = 1 - (ret[12] ** (1 / 12))
ltv = arpu * margen / churn_mensual
tabla = pd.DataFrame({"churn_mensual": churn_mensual, "LTV": ltv, "LTV/CAC": ltv / cac,
                      "payback_meses": cac / (arpu * margen)})
print(tabla.round(2).to_string())
peor = tabla["LTV/CAC"].idxmin()
print(f"Cohorte con menor LTV/CAC: {peor} ({tabla.loc[peor, 'LTV/CAC']:.2f}); regla usual: >= 3")
