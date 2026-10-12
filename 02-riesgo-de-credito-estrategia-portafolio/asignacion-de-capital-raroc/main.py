import numpy as np
import pandas as pd
from scipy.optimize import linprog

segmentos = pd.DataFrame({
    "segmento": ["consumo", "tarjeta", "vehiculo", "hipotecario", "pyme", "corporativo"],
    "margen": [0.140, 0.220, 0.080, 0.055, 0.105, 0.045],
    "perdida_esperada": [0.040, 0.075, 0.012, 0.004, 0.028, 0.006],
    "costo_operativo": [0.030, 0.045, 0.015, 0.010, 0.025, 0.006],
    "capital": [0.100, 0.130, 0.080, 0.050, 0.110, 0.070],
    "tope": [0.30, 0.15, 0.30, 0.40, 0.20, 0.35],
})
segmentos["utilidad"] = segmentos["margen"] - segmentos["perdida_esperada"] - segmentos["costo_operativo"]
segmentos["raroc"] = segmentos["utilidad"] / segmentos["capital"]

presupuesto, capital_disponible = 1.0, 0.085  # 100% de la cartera, 8.5% de capital
c = -segmentos["utilidad"].to_numpy()
A_ub = [segmentos["capital"].to_numpy()]
b_ub = [capital_disponible]
A_eq = [np.ones(len(segmentos))]
b_eq = [presupuesto]
bounds = [(0, t) for t in segmentos["tope"]]
res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

segmentos["asignacion"] = res.x
print(segmentos[["segmento", "utilidad", "capital", "raroc", "tope", "asignacion"]].round(4).to_string(index=False))
util = float(res.x @ segmentos["utilidad"])
cap = float(res.x @ segmentos["capital"])
print(f"Estado del optimizador: {res.message}")
print(f"Utilidad esperada sobre cartera: {util:.4f} | capital usado: {cap:.4f} de {capital_disponible} | RAROC: {util / cap:.3f}")
