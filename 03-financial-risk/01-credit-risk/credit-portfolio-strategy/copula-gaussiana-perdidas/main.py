import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(13)
n = 200
pd_ = rng.uniform(0.005, 0.06, n)
ead = rng.lognormal(10, 0.8, n)
lgd = rng.uniform(0.35, 0.65, n)
rho = rng.uniform(0.08, 0.20, n)
sims = 30_000
umbral = norm.ppf(pd_)


def simular(correlacionado):
    if correlacionado:
        y = rng.standard_normal((sims, 1))
        e = rng.standard_normal((sims, n))
        activo = np.sqrt(rho) * y + np.sqrt(1 - rho) * e
        default = activo < umbral
    else:
        default = rng.random((sims, n)) < pd_
    return (default * lgd * ead).sum(axis=1)


def resumen(perdidas, nombre):
    var = np.quantile(perdidas, 0.999)
    es = perdidas[perdidas >= var].mean()
    print(f"{nombre:16s} EL={perdidas.mean():>11,.0f} VaR99.9={var:>12,.0f} ES99.9={es:>12,.0f}")
    return var


print(f"Exposicion total: {ead.sum():,.0f}")
v_ind = resumen(simular(False), "independientes")
v_cor = resumen(simular(True), "cópula factor")
print(f"El VaR con correlacion es {v_cor / v_ind:.2f}x el de incumplimientos independientes")
