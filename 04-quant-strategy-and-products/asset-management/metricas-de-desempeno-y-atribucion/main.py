import numpy as np
import pandas as pd
import statsmodels.api as sm

rng = np.random.default_rng(47)
dias = 1260
bench = rng.normal(0.0004, 0.010, dias)
port = 0.0001 + 1.1 * bench + rng.normal(0, 0.004, dias)
rf = 0.03 / 252


def metricas(r, bench=None):
    exceso = r - rf
    anual = (1 + r).prod() ** (252 / len(r)) - 1
    vol = r.std(ddof=1) * np.sqrt(252)
    caida = r[r < rf] - rf
    sortino = exceso.mean() * 252 / (np.sqrt((caida ** 2).sum() / len(r)) * np.sqrt(252))
    riqueza = (1 + r).cumprod()
    dd = (riqueza / np.maximum.accumulate(riqueza) - 1).min()
    out = {"retorno_anual": anual, "volatilidad": vol, "sharpe": exceso.mean() * 252 / vol,
           "sortino": sortino, "max_drawdown": dd, "calmar": anual / abs(dd)}
    if bench is not None:
        res = sm.OLS(exceso, sm.add_constant(bench - rf)).fit()
        te = (r - bench).std(ddof=1) * np.sqrt(252)
        out.update({"alfa_anual": res.params[0] * 252, "beta": res.params[1],
                    "tracking_error": te, "information_ratio": ((r - bench).mean() * 252) / te})
    return out


tabla = pd.DataFrame({"portafolio": metricas(port, bench), "benchmark": metricas(bench)})
print(tabla.round(4).to_string())
