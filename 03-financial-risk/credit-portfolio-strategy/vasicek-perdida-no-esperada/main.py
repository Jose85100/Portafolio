import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(9)
PD, LGD, n_deudores, sims, q = 0.02, 0.45, 2000, 200_000, 0.999


def capital_vasicek(pd_, rho, lgd, q):
    pd_cond = norm.cdf((norm.ppf(pd_) + np.sqrt(rho) * norm.ppf(q)) / np.sqrt(1 - rho))
    return lgd * (pd_cond - pd_)


def capital_mc(pd_, rho, lgd, q, n, sims):
    y = rng.standard_normal(sims)
    pd_y = norm.cdf((norm.ppf(pd_) - np.sqrt(rho) * y) / np.sqrt(1 - rho))
    defaults = rng.binomial(n, pd_y)
    perdida = lgd * defaults / n
    return np.quantile(perdida, q) - lgd * pd_


print(f"PD={PD}, LGD={LGD}, deudores={n_deudores}, nivel {q:.1%}")
print(f"{'rho':>5} {'Vasicek':>10} {'Monte Carlo':>12}")
for rho in [0.03, 0.08, 0.15, 0.24]:
    kv = capital_vasicek(PD, rho, LGD, q)
    km = capital_mc(PD, rho, LGD, q, n_deudores, sims)
    print(f"{rho:>5.2f} {kv:>10.4f} {km:>12.4f}")
