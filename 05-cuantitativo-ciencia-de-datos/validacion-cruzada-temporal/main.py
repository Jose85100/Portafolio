import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, TimeSeriesSplit

rng = np.random.default_rng(71)
n = 1500
y = np.zeros(n)
for i in range(1, n):
    y[i] = 0.98 * y[i - 1] + rng.normal()  # serie muy persistente
X = np.arange(n).reshape(-1, 1)  # el unico "predictor" es el indice de tiempo


def evaluar(splitter):
    puntajes = []
    for tr, te in splitter.split(X):
        m = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=-1).fit(X[tr], y[tr])
        puntajes.append(r2_score(y[te], m.predict(X[te])))
    return np.mean(puntajes)


print("Serie persistente sin senal predictiva real (solo indice de tiempo como variable)")
print(f"R2 con KFold aleatorio (con fuga temporal): {evaluar(KFold(5, shuffle=True, random_state=0)):.3f}")
print(f"R2 con TimeSeriesSplit (sin fuga):         {evaluar(TimeSeriesSplit(5)):.3f}")
