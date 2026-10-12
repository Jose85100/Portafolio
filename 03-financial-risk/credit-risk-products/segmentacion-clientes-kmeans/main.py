import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(5)
n = 6000
grupo = rng.choice(3, n, p=[0.5, 0.3, 0.2])
centros = {0: (4000, 0.2, 0.1), 1: (2500, 0.6, 0.6), 2: (1500, 0.9, 1.8)}
base_pd = {0: 0.02, 1: 0.07, 2: 0.22}
df = pd.DataFrame({
    "ingreso": [rng.normal(centros[g][0], 500) for g in grupo],
    "utilizacion": [np.clip(rng.normal(centros[g][1], 0.12), 0, 1.2) for g in grupo],
    "mora_media": [max(0, rng.normal(centros[g][2], 0.4)) for g in grupo],
})
df["default"] = [int(rng.random() < base_pd[g]) for g in grupo]

X = StandardScaler().fit_transform(df[["ingreso", "utilizacion", "mora_media"]])
mejor_k, mejor_s = None, -1
for k in range(2, 7):
    etiquetas = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
    s = silhouette_score(X, etiquetas)
    print(f"k={k}: silueta={s:.3f}")
    if s > mejor_s:
        mejor_k, mejor_s = k, s

df["segmento"] = KMeans(n_clusters=mejor_k, n_init=10, random_state=0).fit_predict(X)
perfil = df.groupby("segmento").agg(
    clientes=("default", "size"),
    ingreso=("ingreso", "mean"),
    utilizacion=("utilizacion", "mean"),
    mora_media=("mora_media", "mean"),
    tasa_default=("default", "mean"),
).sort_values("tasa_default")
print(f"k elegido = {mejor_k}")
print(perfil.round(3).to_string())
