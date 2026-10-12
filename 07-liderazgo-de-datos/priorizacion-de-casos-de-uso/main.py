import numpy as np
import pandas as pd

casos = pd.DataFrame({
    "caso": ["scoring de originacion", "monitoreo de cartera", "deteccion de fraude", "chatbot de servicio",
             "pronostico de liquidez", "segmentacion de clientes", "automatizacion de reportes", "precios dinamicos"],
    "beneficio": [9, 8, 8, 5, 7, 6, 4, 7],
    "ajuste_estrategico": [9, 8, 7, 4, 6, 6, 5, 5],
    "costo": [6, 5, 7, 6, 4, 3, 2, 8],
    "riesgo": [5, 4, 6, 5, 3, 3, 2, 7],
    "preparacion_datos": [6, 8, 5, 3, 7, 8, 9, 4],  # 10 = datos listos
}).set_index("caso")

pesos_valor = {"beneficio": 0.65, "ajuste_estrategico": 0.35}
valor = sum(casos[k] * w for k, w in pesos_valor.items())
esfuerzo = (casos["costo"] * 0.4 + casos["riesgo"] * 0.3 + (10 - casos["preparacion_datos"]) * 0.3)
casos["valor"], casos["esfuerzo"] = valor, esfuerzo
casos["prioridad"] = casos["valor"] / casos["esfuerzo"]
mv, me = casos["valor"].median(), casos["esfuerzo"].median()
casos["cuadrante"] = np.where(casos["valor"] >= mv,
                              np.where(casos["esfuerzo"] <= me, "hacer ya", "proyecto grande"),
                              np.where(casos["esfuerzo"] <= me, "ganancia rapida", "descartar o aplazar"))
print(casos[["valor", "esfuerzo", "prioridad", "cuadrante"]].sort_values("prioridad", ascending=False).round(2).to_string())

rng = np.random.default_rng(103)
top1 = []
for _ in range(2000):
    w = rng.dirichlet([1, 1])
    v = casos["beneficio"] * w[0] + casos["ajuste_estrategico"] * w[1]
    top1.append((v / esfuerzo).idxmax())
print("Caso en primer lugar bajo pesos aleatorios de valor:")
print(pd.Series(top1).value_counts(normalize=True).round(3).to_string())
