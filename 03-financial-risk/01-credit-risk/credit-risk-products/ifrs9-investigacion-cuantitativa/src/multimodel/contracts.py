"""Shared numerical and data contracts. Rates are annual effective; steps monthly."""
from numbers import Integral
import numpy as np


def array(values, name, ndim=1):
    out = np.asarray(values, dtype=float)
    if out.ndim != ndim or out.size == 0 or not np.isfinite(out).all():
        raise ValueError(f'{name}: nonempty finite {ndim}D array required')
    return out


def probabilities(values, name='probabilities', ndim=1):
    out = array(values, name, ndim)
    if ((out < 0) | (out > 1)).any():
        raise ValueError(f'{name}: values must lie in [0,1]')
    return out


def integer(value, name, maximum=600):
    if isinstance(value, bool) or not isinstance(value, Integral) or not 1 <= value <= maximum:
        raise ValueError(f'{name}: integer in [1,{maximum}] required')
    return int(value)


def weights(mapping):
    if not isinstance(mapping, dict) or not mapping or any(not isinstance(k, str) for k in mapping):
        raise ValueError('Named scenario weights required')
    p = probabilities(list(mapping.values()), 'weights')
    if not np.isclose(p.sum(), 1., atol=1e-12, rtol=0):
        raise ValueError('Weights must sum to one')
    return mapping


def default_curve(conditional):
    q = probabilities(conditional, 'conditional monthly PD', 2)
    survival = np.cumprod(1-q, axis=1)
    start = np.column_stack([np.ones(len(q)), survival[:, :-1]])
    return start*q, survival


def frame(frame, columns, name='data'):
    if frame.empty or set(columns)-set(frame) or not frame.index.is_unique:
        raise ValueError(f'{name}: nonempty data, unique index and columns {columns} required')
    for column in columns:
        array(frame[column], column)
    return frame
