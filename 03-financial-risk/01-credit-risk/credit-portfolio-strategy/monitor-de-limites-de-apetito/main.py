import numpy as np
import pandas as pd

rng = np.random.default_rng(31)
n = 400
df = pd.DataFrame({
    "sector": rng.choice(["comercio", "industria", "agro", "servicios", "construccion"], n,
                         p=[0.35, 0.2, 0.1, 0.2, 0.15]),
    "rating": rng.choice(["A", "B", "C", "D"], n, p=[0.25, 0.4, 0.25, 0.10]),
    "exposicion": rng.lognormal(11, 1.0, n),
})
total = df["exposicion"].sum()

limites = [
    ("sector comercio", df.loc[df.sector == "comercio", "exposicion"].sum() / total, 0.30),
    ("sector construccion", df.loc[df.sector == "construccion", "exposicion"].sum() / total, 0.15),
    ("rating C+D", df.loc[df.rating.isin(["C", "D"]), "exposicion"].sum() / total, 0.30),
    ("rating D", df.loc[df.rating == "D", "exposicion"].sum() / total, 0.08),
    ("mayor deudor", df["exposicion"].max() / total, 0.04),
]


def semaforo(uso):
    if uso >= 1.0:
        return "ROJO"
    if uso >= 0.85:
        return "AMBAR"
    return "VERDE"


filas = []
for nombre, valor, limite in limites:
    uso = valor / limite
    filas.append({"limite": nombre, "valor": valor, "tope": limite, "utilizacion": uso, "estado": semaforo(uso)})
tabla = pd.DataFrame(filas)
print(tabla.round(3).to_string(index=False))
print(tabla["estado"].value_counts().to_string())
