import numpy as np
import pandas as pd

valor = 10_000_000
# sensibilidad de la perdida/ganancia (en % del portafolio) por cada 1% de choque en el factor
sens = pd.Series({"acciones": 0.45, "tasa_10y_pb": -0.0062, "usd_cop": 0.12, "spread_credito_pb": -0.0021})
escenarios = pd.DataFrame({
    "crisis_2008":     {"acciones": -38.0, "tasa_10y_pb": -120, "usd_cop": 25.0, "spread_credito_pb": 400},
    "alza_de_tasas":   {"acciones": -12.0, "tasa_10y_pb": 250, "usd_cop": 8.0, "spread_credito_pb": 120},
    "choque_cambiario": {"acciones": -9.0, "tasa_10y_pb": 60, "usd_cop": 30.0, "spread_credito_pb": 90},
    "recesion_local":  {"acciones": -22.0, "tasa_10y_pb": -80, "usd_cop": 15.0, "spread_credito_pb": 250},
}).T

contrib = escenarios.mul(sens, axis=1)
resultado = contrib.copy()
resultado["total_pct"] = contrib.sum(axis=1)
resultado["perdida"] = resultado["total_pct"] / 100 * valor
print(resultado.round(2).to_string())
peor = resultado["total_pct"].idxmin()
print(f"Peor escenario: {peor} ({resultado.loc[peor, 'total_pct']:.2f}% | {resultado.loc[peor, 'perdida']:,.0f})")

objetivo = -10.0
# estres inverso: si solo se mueven acciones y el resto queda en 0
choque = objetivo / sens["acciones"]
print(f"Estres inverso: para perder {abs(objetivo)}% solo con acciones se requiere un choque de {choque:.1f}%")
