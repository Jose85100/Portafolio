import numpy as np

rng = np.random.default_rng(73)
n_fondos, n_inversiones, anos = 20000, 30, 8
# resultados por inversion: (probabilidad, multiplo minimo, multiplo maximo)
tramos = [(0.55, 0.0, 0.0), (0.25, 0.5, 2.0), (0.14, 2.0, 8.0), (0.055, 8.0, 40.0), (0.005, 40.0, 150.0)]
prob = np.array([t[0] for t in tramos])
lo = np.array([t[1] for t in tramos])
hi = np.array([t[2] for t in tramos])

tramo = rng.choice(len(tramos), size=(n_fondos, n_inversiones), p=prob / prob.sum())
multiplos = rng.uniform(lo[tramo], hi[tramo])
moic = multiplos.mean(axis=1)  # inversiones de igual tamano
tir_aprox = np.where(moic > 0, moic ** (1 / anos) - 1, -1.0)

print(f"Fondos simulados: {n_fondos} | inversiones por fondo: {n_inversiones}")
print(f"MOIC mediano: {np.median(moic):.2f}x | media: {moic.mean():.2f}x")
print("Percentiles MOIC (5, 25, 75, 95):", np.percentile(moic, [5, 25, 75, 95]).round(2))
print(f"P(MOIC >= 1x) = {(moic >= 1).mean():.1%} | P(MOIC >= 3x) = {(moic >= 3).mean():.1%}")
print(f"TIR aproximada mediana (horizonte {anos} anos): {np.median(tir_aprox):.1%}")
mejor = np.sort(multiplos, axis=1)[:, -1] / multiplos.sum(axis=1)
print(f"La mejor inversion aporta en mediana el {np.median(mejor):.0%} del valor del fondo")
