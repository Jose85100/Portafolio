import numpy as np
import pandas as pd

rng = np.random.default_rng(89)
n = 1000
clientes = pd.DataFrame({
    "cliente_id": np.arange(n),
    "edad": rng.integers(18, 80, n).astype(float),
    "ingreso": rng.lognormal(8, 0.5, n),
    "ciudad_id": rng.integers(1, 6, n),
    "actualizado": pd.Timestamp("2026-10-01") - pd.to_timedelta(rng.integers(0, 40, n), unit="D"),
})
# problemas inyectados
clientes.loc[rng.choice(n, 40, replace=False), "edad"] = np.nan
clientes.loc[rng.choice(n, 15, replace=False), "edad"] = -3
clientes.loc[rng.choice(n, 25, replace=False), "ingreso"] = -100
clientes.loc[[10, 20, 30], "cliente_id"] = 5
clientes.loc[rng.choice(n, 30, replace=False), "ciudad_id"] = 99
clientes.loc[rng.choice(n, 60, replace=False), "actualizado"] = pd.Timestamp("2026-06-01")
ciudades = {1, 2, 3, 4, 5}
corte = pd.Timestamp("2026-10-12")

reglas = {
    "completitud edad": clientes["edad"].notna(),
    "unicidad cliente_id": ~clientes["cliente_id"].duplicated(keep=False),
    "rango edad 18-100": clientes["edad"].between(18, 100) | clientes["edad"].isna(),
    "ingreso positivo": clientes["ingreso"] > 0,
    "ciudad existe": clientes["ciudad_id"].isin(ciudades),
    "actualizado <= 60 dias": (corte - clientes["actualizado"]).dt.days <= 60,
}
reporte = pd.DataFrame({
    "cumplimiento": {k: v.mean() for k, v in reglas.items()},
    "filas_fallidas": {k: int((~v).sum()) for k, v in reglas.items()},
})
reporte["estado"] = np.where(reporte["cumplimiento"] >= 0.99, "OK", np.where(reporte["cumplimiento"] >= 0.95, "ALERTA", "FALLA"))
print(reporte.round(4).to_string())
calidad = np.mean([v.mean() for v in reglas.values()])
print(f"Indice global de calidad (promedio de reglas): {calidad:.3f}")
