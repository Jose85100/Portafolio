import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
estados = ["al_dia", "mora_30", "mora_60", "mora_90", "default"]
P_true = np.array([
    [0.94, 0.05, 0.00, 0.00, 0.01],
    [0.35, 0.40, 0.25, 0.00, 0.00],
    [0.15, 0.10, 0.35, 0.40, 0.00],
    [0.05, 0.00, 0.10, 0.45, 0.40],
    [0.00, 0.00, 0.00, 0.00, 1.00],
])

n_cuentas, meses = 30000, 24
estado = np.zeros(n_cuentas, dtype=int)
conteos = np.zeros((5, 5))
for _ in range(meses):
    u = rng.random(n_cuentas)
    acumulada = P_true[estado].cumsum(axis=1)
    nuevo = (u[:, None] > acumulada).sum(axis=1)
    np.add.at(conteos, (estado, nuevo), 1)
    estado = nuevo

P_hat = conteos / conteos.sum(axis=1, keepdims=True)
print("Matriz estimada (filas = estado actual):")
print(pd.DataFrame(P_hat, index=estados, columns=estados).round(3).to_string())
print(f"Error absoluto maximo vs matriz verdadera: {np.abs(P_hat - P_true).max():.4f}")

pd12_hat = np.linalg.matrix_power(P_hat, 12)[0, 4]
pd12_true = np.linalg.matrix_power(P_true, 12)[0, 4]
print(f"PD acumulada a 12 meses (cuenta al dia): estimada {pd12_hat:.4f} | verdadera {pd12_true:.4f}")
