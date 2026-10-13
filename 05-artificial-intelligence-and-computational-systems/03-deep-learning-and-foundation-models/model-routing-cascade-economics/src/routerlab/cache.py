"""Cache semantico simulado: una consulta reutiliza una respuesta previa si su embedding es suficientemente parecido."""
from __future__ import annotations
import numpy as np


def simulate_cache(n: int, n_intents: int, noise: float, tau: float, rng: np.random.Generator, dim: int = 16, zipf_a: float = 1.2, capacity: int | None = None) -> dict:
    """Flujo de `n` consultas con intenciones Zipf; embedding = centro de la intencion (unitario) + ruido gaussiano de escala `noise`.
    Acierto de cache si max coseno >= tau; el acierto es CORRECTO solo si la consulta guardada tiene la misma intencion.
    Cada fallo de cache se responde con el modelo y se guarda. Devuelve tasa de aciertos, tasa de error entre aciertos y fraccion de llamadas ahorradas."""
    centros = rng.standard_normal((n_intents, dim)); centros /= np.linalg.norm(centros, axis=1, keepdims=True)
    p = 1.0 / np.arange(1, n_intents + 1) ** zipf_a; p /= p.sum(); intents = rng.choice(n_intents, n, p=p)
    E = centros[intents] + noise * rng.standard_normal((n, dim)) / np.sqrt(dim); E /= np.linalg.norm(E, axis=1, keepdims=True)
    cache_e = np.zeros((0, dim)); cache_i = np.zeros(0, int); hits = errores = 0
    for k in range(n):
        if len(cache_i):
            sim = cache_e @ E[k]; j = int(np.argmax(sim))
            if sim[j] >= tau: hits += 1; errores += int(cache_i[j] != intents[k]); continue
        cache_e = np.vstack([cache_e, E[k]]); cache_i = np.r_[cache_i, intents[k]]
        if capacity and len(cache_i) > capacity: cache_e, cache_i = cache_e[1:], cache_i[1:]
    return {"hit_rate": hits / n, "error_rate_on_hits": errores / hits if hits else 0.0, "wrong_answers": errores / n, "calls_saved": hits / n}
