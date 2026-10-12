"""Modelo gaussiano de un factor: pérdidas, VaR y Expected Shortfall.

Supuestos: PD marginales incondicionales, LGD/EAD deterministas, un factor
sistemático normal, errores idiosincráticos normales independientes.
No representa correlación de LGD/EAD ni dependencia de colas no gaussiana.
"""
from dataclasses import dataclass
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class Resultados:
    perdida_esperada_analitica: float
    perdida_esperada_montecarlo: float
    var: float
    expected_shortfall: float
    capital_economico: float
    error_estandar_media: float


def simular_perdidas(pd, lgd, ead, rho, *, simulaciones=100_000,
                     semilla=42, tamano_lote=5_000):
    """Simula pérdidas sin almacenar una matriz de tamaño simulaciones x créditos.

    rho representa la correlación de activos con un único factor común.
    """
    pd = np.asarray(pd, dtype=float)
    lgd = np.asarray(lgd, dtype=float)
    ead = np.asarray(ead, dtype=float)
    rho = np.asarray(rho, dtype=float)
    if pd.ndim != 1 or pd.size == 0:
        raise ValueError("pd debe ser un vector no vacío")
    if any(x.shape != pd.shape for x in (lgd, ead, rho)):
        raise ValueError("pd, lgd, ead y rho deben tener igual dimensión")
    if (not np.all(np.isfinite(pd)) or not np.all(np.isfinite(lgd))
            or not np.all(np.isfinite(ead)) or not np.all(np.isfinite(rho))):
        raise ValueError("Todos los parámetros deben ser finitos")
    if (np.any((pd < 0) | (pd > 1))
            or np.any((lgd < 0) | (lgd > 1))
            or np.any(ead < 0)
            or np.any((rho < 0) | (rho >= 1))):
        raise ValueError("Parámetros fuera de dominio")
    if not isinstance(simulaciones, (int, np.integer)) or simulaciones < 2:
        raise ValueError("simulaciones debe ser entero >= 2")
    if not isinstance(tamano_lote, (int, np.integer)) or tamano_lote < 1:
        raise ValueError("tamano_lote debe ser entero positivo")

    rng = np.random.default_rng(semilla)
    umbrales = norm.ppf(pd)
    pesos = lgd * ead
    raiz_rho = np.sqrt(rho)
    raiz_idio = np.sqrt(1.0 - rho)
    perdidas = np.empty(simulaciones)
    for inicio in range(0, simulaciones, tamano_lote):
        fin = min(inicio + tamano_lote, simulaciones)
        n = fin - inicio
        z = rng.standard_normal((n, 1))
        eps = rng.standard_normal((n, pd.size))
        activos = z * raiz_rho + eps * raiz_idio
        perdidas[inicio:fin] = ((activos < umbrales) * pesos).sum(axis=1)
    return perdidas


def metricas(perdidas, pd, lgd, ead, *, confianza=0.999):
    """ES empírico como media del peor (1-confianza) de escenarios.

    Se utiliza la cola superior ordenada con ponderación fraccional del
    escenario de frontera; esto evita sesgo por empates en distribuciones
    discretas y coincide con la definición integral del ES empírico.
    """
    l = np.asarray(perdidas, dtype=float)
    if l.ndim != 1 or l.size < 2 or not np.all(np.isfinite(l)):
        raise ValueError("Se necesitan al menos dos pérdidas finitas")
    if not 0 < confianza < 1:
        raise ValueError("confianza debe estar entre 0 y 1")
    p = np.asarray(pd, dtype=float)
    g = np.asarray(lgd, dtype=float)
    e = np.asarray(ead, dtype=float)
    if p.ndim != 1 or p.size == 0 or g.shape != p.shape or e.shape != p.shape:
        raise ValueError("Vectores de exposición incompatibles")
    if not all(np.all(np.isfinite(x)) for x in (p, g, e)):
        raise ValueError("Parámetros no finitos")
    if np.any((p < 0) | (p > 1)) or np.any((g < 0) | (g > 1)) or np.any(e < 0):
        raise ValueError("Parámetros fuera de dominio")
    orden = np.sort(l)
    n = len(orden)
    cola = (1.0 - confianza) * n
    completos = int(np.floor(cola))
    fraccion = cola - completos
    suma = orden[-completos:].sum() if completos else 0.0
    if fraccion > 0:
        suma += fraccion * orden[-completos - 1]
    es = suma / cola
    var = float(np.quantile(l, confianza))
    el = float(np.sum(p * g * e))
    return Resultados(
        perdida_esperada_analitica=el,
        perdida_esperada_montecarlo=float(l.mean()),
        var=var,
        expected_shortfall=float(es),
        capital_economico=max(0.0, var - el),
        error_estandar_media=float(l.std(ddof=1) / np.sqrt(n)),
    )


if __name__ == "__main__":
    rng = np.random.default_rng(13)
    n = 200
    pd = rng.uniform(0.005, 0.06, n)
    ead = rng.lognormal(10, 0.8, n)
    lgd = rng.uniform(0.35, 0.65, n)
    rho = rng.uniform(0.08, 0.20, n)
    for etiqueta, correlacion in [("independiente", np.zeros(n)),
                                  ("factor común", rho)]:
        l = simular_perdidas(pd, lgd, ead, correlacion, simulaciones=50_000)
        r = metricas(l, pd, lgd, ead)
        print(etiqueta, r)
