import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(67)
S0, K, T, r, sigma = 100.0, 105.0, 1.0, 0.04, 0.25


def black_scholes(S0, K, T, r, sigma):
    d1 = (np.log(S0 / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2), norm.cdf(d1)


def monte_carlo(n, antitetico):
    z = rng.standard_normal(n // 2 if antitetico else n)
    if antitetico:
        z = np.r_[z, -z]
    ST = S0 * np.exp((r - sigma ** 2 / 2) * T + sigma * np.sqrt(T) * z)
    pago = np.exp(-r * T) * np.maximum(ST - K, 0)
    delta = np.exp(-r * T) * (ST > K) * ST / S0
    return pago.mean(), pago.std(ddof=1) / np.sqrt(len(pago)), delta.mean()


precio, delta_bs = black_scholes(S0, K, T, r, sigma)
print(f"Black-Scholes: precio={precio:.4f} delta={delta_bs:.4f}")
print(f"{'n':>9} {'tipo':>10} {'precio_MC':>10} {'err_std':>9} {'delta_MC':>9}")
for n in (1_000, 10_000, 100_000, 1_000_000):
    for antitetico in (False, True):
        p, se, d = monte_carlo(n, antitetico)
        print(f"{n:>9} {'antitetico' if antitetico else 'simple':>10} {p:>10.4f} {se:>9.4f} {d:>9.4f}")
