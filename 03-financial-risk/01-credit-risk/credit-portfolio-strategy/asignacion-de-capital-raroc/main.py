"""Asignación de cartera: RAROC máximo y utilidad máxima.

Los insumos son sintéticos y expresados por unidad de exposición. El modelo
RAROC se resuelve exactamente como un programa lineal fraccional mediante la
transformación de Charnes--Cooper; no confunde maximizar utilidad con maximizar
utilidad/capital.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog


def segmentos_sinteticos() -> pd.DataFrame:
    """Devuelve los supuestos ilustrativos, sin datos de clientes."""
    data = pd.DataFrame({
        "segmento": ["consumo", "tarjeta", "vehiculo", "hipotecario", "pyme", "corporativo"],
        "margen": [0.140, 0.220, 0.080, 0.055, 0.105, 0.045],
        "perdida_esperada": [0.040, 0.075, 0.012, 0.004, 0.028, 0.006],
        "costo_operativo": [0.030, 0.045, 0.015, 0.010, 0.025, 0.006],
        "capital": [0.100, 0.130, 0.080, 0.050, 0.110, 0.070],
        "tope": [0.30, 0.15, 0.30, 0.40, 0.20, 0.35],
    })
    data["utilidad"] = data["margen"] - data["perdida_esperada"] - data["costo_operativo"]
    data["raroc_individual"] = data["utilidad"] / data["capital"]
    return data


def asignar_max_raroc(segmentos: pd.DataFrame, capital_disponible: float) -> np.ndarray:
    """Maximiza ``pi'x / k'x`` con cartera totalmente invertida y topes.

    Para ``y=x/(k'x)`` y ``t=1/(k'x)``, el problema fraccional es:
    ``max pi'y`` sujeto a ``1'y=t``, ``k'y=1``, ``Kt>=1`` y
    ``0<=y_i<=tope_i*t``. El resultado se recupera como ``x=y/t``.
    """
    utilidad, capital, tope = (segmentos[col].to_numpy() for col in ("utilidad", "capital", "tope"))
    n = len(segmentos)
    c = np.r_[-utilidad, 0.0]
    a_eq = np.vstack([np.r_[np.ones(n), -1.0], np.r_[capital, 0.0]])
    a_ub = np.vstack([np.r_[np.zeros(n), -capital_disponible],
                      *[np.r_[np.eye(n)[i], -tope[i]] for i in range(n)]])
    resultado = linprog(c, A_ub=a_ub, b_ub=np.r_[-1.0, np.zeros(n)],
                         A_eq=a_eq, b_eq=[0.0, 1.0], bounds=[(0, None)] * (n + 1), method="highs")
    if not resultado.success:
        raise RuntimeError(f"No fue posible resolver RAROC: {resultado.message}")
    return resultado.x[:n] / resultado.x[-1]


def asignar_max_utilidad(segmentos: pd.DataFrame, capital_disponible: float) -> np.ndarray:
    """Referencia distinta: maximiza utilidad esperada, no RAROC."""
    resultado = linprog(-segmentos["utilidad"].to_numpy(), A_ub=[segmentos["capital"].to_numpy()],
                         b_ub=[capital_disponible], A_eq=[np.ones(len(segmentos))], b_eq=[1.0],
                         bounds=[(0, tope) for tope in segmentos["tope"]], method="highs")
    if not resultado.success:
        raise RuntimeError(f"No fue posible resolver utilidad: {resultado.message}")
    return resultado.x


def metricas(segmentos: pd.DataFrame, pesos: np.ndarray) -> dict[str, float]:
    utilidad = float(pesos @ segmentos["utilidad"])
    capital = float(pesos @ segmentos["capital"])
    return {"utilidad": utilidad, "capital": capital, "raroc": utilidad / capital}


def main() -> None:
    segmentos, capital_disponible = segmentos_sinteticos(), 0.085
    x_raroc = asignar_max_raroc(segmentos, capital_disponible)
    x_utilidad = asignar_max_utilidad(segmentos, capital_disponible)
    salida = segmentos[["segmento", "utilidad", "capital", "raroc_individual", "tope"]].copy()
    salida["max_raroc"], salida["max_utilidad"] = x_raroc, x_utilidad
    print(salida.round(4).to_string(index=False))
    for nombre, pesos in [("Máximo RAROC", x_raroc), ("Máxima utilidad", x_utilidad)]:
        m = metricas(segmentos, pesos)
        print(f"{nombre:16s} | utilidad={m['utilidad']:.4f} | capital={m['capital']:.4f} | RAROC={m['raroc']:.3f}")


if __name__ == "__main__":
    main()
