import numpy as np
import pandas as pd

activos = ["EEUU", "Europa", "Japon", "Emergentes", "Bonos"]
w_mkt = np.array([0.38, 0.17, 0.08, 0.10, 0.27])
vol = np.array([0.16, 0.18, 0.17, 0.22, 0.06])
corr = np.array([
    [1.00, 0.80, 0.65, 0.70, 0.00],
    [0.80, 1.00, 0.65, 0.72, 0.05],
    [0.65, 0.65, 1.00, 0.60, 0.05],
    [0.70, 0.72, 0.60, 1.00, 0.00],
    [0.00, 0.05, 0.05, 0.00, 1.00],
])
cov = np.outer(vol, vol) * corr
delta, tau = 2.5, 0.05

pi = delta * cov @ w_mkt  # retornos de equilibrio implicitos

# opiniones: (1) Emergentes superan a EEUU por 3%, (2) Europa rinde 8% absoluto
P = np.array([[-1, 0, 0, 1, 0],
              [0, 1, 0, 0, 0]], dtype=float)
Q = np.array([0.03, 0.08])
omega = np.diag(np.diag(P @ (tau * cov) @ P.T))

inv = np.linalg.inv
mu_bl = inv(inv(tau * cov) + P.T @ inv(omega) @ P) @ (inv(tau * cov) @ pi + P.T @ inv(omega) @ Q)
w_bl = inv(delta * cov) @ mu_bl
w_bl = w_bl / w_bl.sum()

tabla = pd.DataFrame({"peso_mercado": w_mkt, "retorno_equilibrio": pi, "retorno_posterior": mu_bl,
                      "peso_BL": w_bl}, index=activos)
print(tabla.round(4).to_string())
print("Cambio de peso vs mercado:", dict(zip(activos, (w_bl - w_mkt).round(3).tolist())))
