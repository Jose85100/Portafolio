"""Finite-q tail conditional probability by two integral coordinates."""

import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad
from scipy.stats import norm, t

from src.copulas import Copula, conditional_values, threshold


def conditional_second_moment(model: Copula, q: float) -> float:
    """Second moment of the conditional Monte Carlo summand, not of raw losses."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", IntegrationWarning)
        value, _ = quad(
            lambda u: float(conditional_values(model, q, np.array([u]))[0]) ** 2,
            0,
            1,
            epsabs=1e-10,
            epsrel=1e-10,
            limit=300,
        )
    return float(value)


def tail_coordinate_reference(model: Copula, q: float) -> tuple[float, float]:
    """Integrate P(Y>a|X) over the truncated marginal distribution of X."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", IntegrationWarning)
        value, error = quad(
            lambda u: float(conditional_values(model, q, np.array([u]))[0]),
            0,
            1,
            epsabs=1e-10,
            epsrel=1e-10,
            limit=300,
        )
    return float(value), float(error)


def latent_coordinate_reference(model: Copula, q: float) -> tuple[float, float]:
    """Independent integrand in latent x; no call to conditional_values."""
    a = threshold(model, q)
    if model.df is None:

        def integrand(x: float) -> float:
            return float(norm.pdf(x) * norm.sf((a - model.rho * x) / np.sqrt(1 - model.rho**2)))
    else:
        df = model.df

        def integrand(x: float) -> float:
            scale = np.sqrt((df + x * x) * (1 - model.rho**2) / (df + 1))
            return float(t.pdf(x, df) * t.sf((a - model.rho * x) / scale, df + 1))

    with warnings.catch_warnings():
        warnings.simplefilter("error", IntegrationWarning)
        value, error = quad(integrand, a, np.inf, epsabs=1e-13, epsrel=1e-10, limit=300)
    return float(value / (1 - q)), float(error / (1 - q))
