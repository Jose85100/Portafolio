"""Laboratorio de riesgo de mercado y liquidez con escenarios sintéticos.

No estima LCR/NSFR ni capital regulatorio. NumPy requerido.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class TailRisk:
    var: float
    es: float
    mean: float


def tail_risk(losses, alpha=0.975):
    """ES de la distribución empírica: masa exacta en la cola con frontera fraccional."""
    x = np.asarray(losses, dtype=float)
    if x.ndim != 1 or x.size < 2 or not np.all(np.isfinite(x)):
        raise ValueError("Se requieren al menos dos pérdidas finitas")
    if not (0 < alpha < 1):
        raise ValueError("alpha fuera de (0,1)")
    ordered = np.sort(x)
    n = len(ordered)
    mass = n * (1 - alpha)
    whole = int(np.floor(mass))
    fractional = mass - whole
    tail_sum = float(ordered[-whole:].sum()) if whole else 0.0
    if fractional > 0:
        tail_sum += fractional * ordered[-whole - 1]
    return TailRisk(float(np.quantile(x, alpha)), tail_sum / mass,
                    float(x.mean()))


@dataclass(frozen=True)
class LiquidityResult:
    paths: np.ndarray
    first_breach: np.ndarray
    breach_probability: float
    max_shortfall: np.ndarray


def liquidity_paths(initial_cash, inflows, outflows, margin_calls=None):
    """Matriz de escenarios x periodos. Primer déficit contado desde periodo 1.

    El primer déficit se define como caja estrictamente negativa.
    No se repone automáticamente caja después del déficit.
    """
    ins = np.asarray(inflows, dtype=float)
    outs = np.asarray(outflows, dtype=float)
    if ins.ndim != 2 or ins.shape != outs.shape or ins.size == 0:
        raise ValueError("inflows/outflows: matrices no vacías e iguales")
    if margin_calls is None:
        margin = np.zeros_like(ins)
    else:
        margin = np.asarray(margin_calls, dtype=float)
    if margin.shape != ins.shape:
        raise ValueError("margin_calls incompatible")
    if not np.isfinite(initial_cash) or initial_cash < 0:
        raise ValueError("initial_cash debe ser finito y no negativo")
    if not all(np.all(np.isfinite(a)) and np.all(a >= 0)
               for a in (ins, outs, margin)):
        raise ValueError("Los flujos deben ser finitos y no negativos")
    paths = initial_cash + np.cumsum(ins - outs - margin, axis=1)
    breached = paths < 0
    any_breach = breached.any(axis=1)
    first = np.where(any_breach, breached.argmax(axis=1) + 1,
                     paths.shape[1] + 1)
    return LiquidityResult(paths, first, float(any_breach.mean()),
                           np.maximum(0, -np.min(paths, axis=1)))


def correlated_stress(n_scenarios=20_000, horizon=30, seed=23,
                      initial_cash=100.0):
    """Shocks normales compartidos: retorno adverso y salida de caja.

    Parámetros arbitrarios en unidades monetarias abstractas. No calibrado.
    """
    if n_scenarios < 2 or horizon < 1:
        raise ValueError("Escenarios >=2, horizonte >=1")
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n_scenarios, horizon))
    independent = rng.standard_normal((n_scenarios, horizon))
    returns = -0.01 * z + 0.006 * independent
    # Mayor shock positivo z -> peor retorno y mayor salida de liquidez.
    outflows = np.maximum(0, 4.0 + 1.2 * z)
    inflows = np.full_like(outflows, 3.5)
    margin = np.maximum(0, 1.5 * z)
    liquidity = liquidity_paths(initial_cash, inflows, outflows, margin)
    market_losses = -1000.0 * returns.sum(axis=1)
    return market_losses, liquidity


def interaction_effect(base, market_only, liquidity_only, joint):
    """Diferencia cruzada de pérdidas en unidades homogéneas."""
    values = np.asarray([base, market_only, liquidity_only, joint], dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("Pérdidas no finitas")
    return float(joint - market_only - liquidity_only + base)


if __name__ == "__main__":
    market, liquidity = correlated_stress()
    tail = tail_risk(market)
    print(f"VaR97.5={tail.var:.4f} ES97.5={tail.es:.4f}")
    print(f"P(deficit de caja en 30 periodos)={liquidity.breach_probability:.4f}")
