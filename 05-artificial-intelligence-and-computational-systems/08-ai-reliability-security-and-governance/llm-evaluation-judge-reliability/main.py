"""Demostracion corta: un juez sesgado, su correccion con PPI y el tamano de muestra de una comparacion pareada."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from evalkit import stats as S, world as W

p, N, n, R = 0.55, 5000, 100, 500; est = {"juez crudo": [], "solo oro (100 etiquetas)": [], "PPI": []}
for r in range(R):
    rg = np.random.default_rng(r); y = (rg.random(N + n) < p).astype(int); j = W.judge_labels(y, np.zeros(len(y)), rg, tpr=0.95, tnr=0.70)
    est["juez crudo"].append(j.mean()); est["solo oro (100 etiquetas)"].append(y[N:].mean()); est["PPI"].append(S.ppi_mean(j[:N], j[N:], y[N:])[0])
print(f"tasa verdadera {p} | {R} repeticiones")
for k, v in est.items(): v = np.array(v); print(f"  {k:26s} media {v.mean():.3f}  sesgo {v.mean() - p:+.3f}  RMSE {np.sqrt(((v - p) ** 2).mean()):.3f}")
print("Wilson 8/10:", tuple(round(float(x), 3) for x in S.wilson_ci(8, 10)), "| Wald 0/20:", tuple(float(x) for x in S.wald_ci(0, 20)), "(degenerado)")
print("pares para detectar 5 puntos con 20% de discordancia:", S.n_paired_binary(0.125, 0.075), "| diseno independiente:", S.n_two_prop(0.65, 0.60))
