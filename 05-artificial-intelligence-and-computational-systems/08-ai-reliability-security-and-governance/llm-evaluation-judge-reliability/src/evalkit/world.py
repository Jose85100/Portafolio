"""Mundos simulados para validar los metodos con verdad conocida: modelos (IRT), jueces con sesgos y comparaciones por pares."""
from __future__ import annotations
import numpy as np


def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))


def logit(p): p = np.clip(p, 1e-9, 1 - 1e-9); return np.log(p / (1 - p))


def make_items(n: int, rng: np.random.Generator) -> dict:
    """Items con dificultad b ~ N(0,1) y 'verbosidad' v ~ N(0,1) de la respuesta."""
    return {"difficulty": rng.standard_normal(n), "verbosity": rng.standard_normal(n)}


def p_correct(theta: float, difficulty: np.ndarray, slope: float = 1.5) -> np.ndarray:
    """Modelo logistico de un parametro: P(acierto) = sigmoid(slope * (theta - dificultad))."""
    return sigmoid(slope * (theta - np.asarray(difficulty)))


def sample_correct(theta: float, items: dict, rng: np.random.Generator, slope: float = 1.5, k: int = 1) -> np.ndarray:
    """Aciertos verdaderos (n x k): k muestras por item (misma dificultad => correlacion dentro del item)."""
    p = p_correct(theta, items["difficulty"], slope)[:, None]; return (rng.random((len(p), k)) < p).astype(int)


def judge_labels(truth: np.ndarray, verbosity: np.ndarray, rng: np.random.Generator, tpr: float = 0.9, tnr: float = 0.85, verbosity_bias: float = 0.0) -> np.ndarray:
    """Etiquetas de un juez automatico. Base: P(pasa | verdad=1)=tpr, P(pasa | verdad=0)=1-tnr. `verbosity_bias` desplaza el logit
    en proporcion a la verbosidad (los jueces suelen favorecer respuestas largas), lo que viola el supuesto de error constante."""
    base = np.where(truth == 1, tpr, 1 - tnr); p = sigmoid(logit(base) + verbosity_bias * np.asarray(verbosity)); return (rng.random(len(p)) < p).astype(int)


def pairwise_judge(q_a: np.ndarray, q_b: np.ndarray, rng: np.random.Generator, position_bias: float = 0.0, sharp: float = 2.0, swapped: bool = False) -> np.ndarray:
    """Juez de comparacion por pares. Devuelve 1 si prefiere A (el primero que ve el juez, salvo swapped=True, donde ve B primero).
    P(prefiere el primero) = sigmoid(sharp * (q_primero - q_segundo) + logit_sesgo_posicion)."""
    first, second = (q_b, q_a) if swapped else (q_a, q_b); p_first = sigmoid(sharp * (first - second) + position_bias)
    pref_first = rng.random(len(p_first)) < p_first; return (~pref_first).astype(int) if swapped else pref_first.astype(int)
