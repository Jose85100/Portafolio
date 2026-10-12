import numpy as np
import pandas as pd

rng = np.random.default_rng(21)
n = 500
sectores = ["comercio", "industria", "agro", "servicios", "construccion", "energia", "transporte", "tecnologia"]
pesos_sector = np.array([0.30, 0.18, 0.12, 0.14, 0.10, 0.06, 0.06, 0.04])
df = pd.DataFrame({
    "deudor": [f"D{i:03d}" for i in range(n)],
    "sector": rng.choice(sectores, n, p=pesos_sector),
    "exposicion": rng.lognormal(12, 1.1, n),
})


def hhi(pesos):
    w = np.asarray(pesos) / np.sum(pesos)
    return float((w ** 2).sum())


h_deudor = hhi(df["exposicion"])
por_sector = df.groupby("sector")["exposicion"].sum().sort_values(ascending=False)
h_sector = hhi(por_sector)
top10 = df["exposicion"].nlargest(10).sum() / df["exposicion"].sum()
mayor = df["exposicion"].max() / df["exposicion"].sum()

print(f"HHI por deudor: {h_deudor:.4f} | numero efectivo de deudores: {1 / h_deudor:.0f} de {n}")
print(f"HHI por sector: {h_sector:.4f} | numero efectivo de sectores: {1 / h_sector:.1f} de {len(sectores)}")
print(f"Participacion top 10 deudores: {top10:.1%} | mayor deudor: {mayor:.2%}")
print("Participacion por sector:")
print((por_sector / por_sector.sum()).round(3).to_string())

limites = {"mayor deudor <= 5%": mayor <= 0.05, "top 10 <= 25%": top10 <= 0.25,
           "mayor sector <= 30%": (por_sector.iloc[0] / por_sector.sum()) <= 0.30}
for nombre, ok in limites.items():
    print(f"  {nombre}: {'CUMPLE' if ok else 'EXCEDE'}")
