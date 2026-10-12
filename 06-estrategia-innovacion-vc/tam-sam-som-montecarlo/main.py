import numpy as np
import pandas as pd

rng = np.random.default_rng(83)
n = 100_000
empresas = rng.triangular(40_000, 55_000, 80_000, n)        # empresas objetivo en el pais
fraccion_elegible = rng.beta(8, 12, n)                       # que cumplen el perfil
precio_anual = rng.lognormal(np.log(3_600), 0.25, n)         # USD por cliente
penetracion = rng.beta(2, 38, n)                             # alcanzable a 5 anos
capacidad = rng.triangular(150, 300, 600, n)                 # clientes por capacidad comercial

tam = empresas * precio_anual
sam = empresas * fraccion_elegible * precio_anual
clientes_som = np.minimum(empresas * fraccion_elegible * penetracion, capacidad)
som = clientes_som * precio_anual

fmt = lambda x: f"{np.percentile(x, 10) / 1e6:7.1f} | {np.percentile(x, 50) / 1e6:7.1f} | {np.percentile(x, 90) / 1e6:7.1f}"
print("Millones de USD por ano  P10 | P50 | P90")
print(f"TAM: {fmt(tam)}")
print(f"SAM: {fmt(sam)}")
print(f"SOM: {fmt(som)}")

vars_ = pd.DataFrame({"empresas": empresas, "elegible": fraccion_elegible, "precio": precio_anual,
                      "penetracion": penetracion, "capacidad": capacidad})
corr = vars_.apply(lambda c: np.corrcoef(c, som)[0, 1]).abs().sort_values(ascending=False)
print("Correlacion absoluta con el SOM:")
print(corr.round(3).to_string())
