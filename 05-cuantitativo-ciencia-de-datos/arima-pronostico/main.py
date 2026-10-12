import itertools
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
rng = np.random.default_rng(61)
n = 240
t = np.arange(n)
ar = np.zeros(n)
for i in range(1, n):
    ar[i] = 0.6 * ar[i - 1] + rng.normal(0, 1.0)
serie = pd.Series(50 + 0.15 * t + 6 * np.sin(2 * np.pi * t / 12) + ar,
                  index=pd.period_range("2006-01", periods=n, freq="M"))
h = 24
train, test = serie.iloc[:-h], serie.iloc[-h:]

mejor, mejor_aic = None, np.inf
for p, d, q in itertools.product(range(3), range(2), range(3)):
    try:
        res = SARIMAX(train, order=(p, d, q), seasonal_order=(1, 0, 0, 12)).fit(disp=False)
    except Exception:
        continue
    if res.aic < mejor_aic:
        mejor, mejor_aic, orden = res, res.aic, (p, d, q)

pron = mejor.forecast(h)
ingenuo = train.iloc[-12:].to_numpy()
ingenuo = np.tile(ingenuo, h // 12 + 1)[:h]
rmse = lambda a, b: float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
print(f"Orden elegido por AIC: ARIMA{orden} x (1,0,0,12) | AIC={mejor_aic:.1f}")
print(f"RMSE modelo   = {rmse(test, pron):.3f}")
print(f"RMSE ingenuo estacional = {rmse(test, ingenuo):.3f}")
