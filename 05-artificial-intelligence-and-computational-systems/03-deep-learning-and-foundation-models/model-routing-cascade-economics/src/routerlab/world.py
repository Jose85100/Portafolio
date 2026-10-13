"""Mundo simulado: consultas con dificultad latente, niveles de modelo con costo y habilidad, y una senal de confianza."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.stats import norm


def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))
def logit(p): p = np.clip(p, 1e-9, 1 - 1e-9); return np.log(p / (1 - p))


@dataclass(frozen=True)
class ModelTier:
    name: str
    cost_per_call: float
    latency_ms: float
    skill: float        # habilidad: P(acierto) = sigmoid(slope * (skill - dificultad))


DEFAULT_TIERS = (ModelTier("small", 1.0, 200.0, -0.3), ModelTier("medium", 6.0, 700.0, 0.6), ModelTier("large", 30.0, 2200.0, 1.6))


class World:
    """Genera consultas con dificultad d ~ N(0,1), cinco atributos observables correlacionados con d y, por nivel:
    p_<t> (probabilidad verdadera), correct_<t> (resultado), conf_<t> (confianza).

    Los resultados de los niveles comparten un factor latente (`rho`): son correlacionados pero no anidados, y se sortean UNA vez por
    consulta (numeros aleatorios comunes), de modo que las politicas se comparan sobre las mismas realizaciones.
    conf_kind: 'calibrated' (conf = p + ruido) u 'overconfident' (conf = sigmoid(k * logit(p)) + ruido, con k>1: valores mas extremos que la verdad).
    """
    def __init__(self, tiers=DEFAULT_TIERS, slope: float = 1.5, feature_noise: float = 1.0, conf_kind: str = "calibrated", conf_noise: float = 0.08, overconfidence: float = 2.0, rho: float = 0.5):
        self.tiers, self.slope, self.fn, self.kind, self.cn, self.k, self.rho = list(tiers), slope, feature_noise, conf_kind, conf_noise, overconfidence, rho
        if conf_kind not in ("calibrated", "overconfident"): raise ValueError(conf_kind)

    def p_correct(self, tier: ModelTier, d): return sigmoid(self.slope * (tier.skill - np.asarray(d)))

    def sample(self, n: int, rng: np.random.Generator) -> pd.DataFrame:
        d = rng.standard_normal(n); out = {"difficulty": d}
        F = np.column_stack([d + self.fn * rng.standard_normal(n), 0.5 * d + self.fn * rng.standard_normal(n), -0.5 * d + self.fn * rng.standard_normal(n), rng.standard_normal(n), rng.standard_normal(n)])
        for j in range(5): out[f"f{j}"] = F[:, j]
        shared = rng.standard_normal(n)
        for t in self.tiers:
            p = self.p_correct(t, d); u = norm.cdf(np.sqrt(self.rho) * shared + np.sqrt(1 - self.rho) * rng.standard_normal(n))
            out[f"p_{t.name}"] = p; out[f"correct_{t.name}"] = (u < p).astype(int)
            base = p if self.kind == "calibrated" else sigmoid(self.k * logit(p)); out[f"conf_{t.name}"] = np.clip(base + self.cn * rng.standard_normal(n), 0.0, 1.0)
        return pd.DataFrame(out)

    def costs(self) -> dict: return {t.name: t.cost_per_call for t in self.tiers}
    def latencies(self) -> dict: return {t.name: t.latency_ms for t in self.tiers}
