import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
n_cosechas, n_creditos, horizonte = 12, 3000, 18
meses_book = np.arange(1, horizonte + 1)
# forma de la hazard: sube hasta el mes 8 y luego decae
forma = meses_book / 8 * np.exp(1 - meses_book / 8)
calidad = rng.normal(1.0, 0.18, n_cosechas)
calidad[8] = 1.55  # una cosecha deteriorada a proposito

curvas = {}
for c in range(n_cosechas):
    hazard = 0.0045 * calidad[c] * forma
    vivos = np.ones(n_creditos, dtype=bool)
    acum = []
    for h in hazard:
        cae = vivos & (rng.random(n_creditos) < h)
        vivos &= ~cae
        acum.append(1 - vivos.mean())
    curvas[f"V{c + 1:02d}"] = acum

tabla = pd.DataFrame(curvas, index=meses_book)
resumen = pd.DataFrame({
    "default_6m": tabla.loc[6],
    "default_12m": tabla.loc[12],
    "default_18m": tabla.loc[18],
})
print(resumen.round(4).to_string())
prom = tabla.loc[12].mean()
peor = tabla.loc[12].idxmax()
print(f"Promedio a 12 meses: {prom:.4f}")
print(f"Peor cosecha: {peor} con {tabla.loc[12, peor]:.4f} ({tabla.loc[12, peor] / prom:.2f}x el promedio)")
