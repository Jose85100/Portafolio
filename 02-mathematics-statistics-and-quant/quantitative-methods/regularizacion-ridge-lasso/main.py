import numpy as np
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(53)
n, p, relevantes = 200, 60, 6
beta = np.zeros(p)
beta[:relevantes] = [3, -2, 1.5, 1, -1, 0.8]
X = rng.standard_normal((n + 2000, p))
X[:, 6:] += 0.5 * X[:, [0]]  # correlacion con una variable relevante
y = X @ beta + rng.normal(0, 2.0, n + 2000)
Xtr, ytr, Xte, yte = X[:n], y[:n], X[n:], y[n:]

modelos = {
    "OLS": LinearRegression().fit(Xtr, ytr),
    "Ridge": RidgeCV(alphas=np.logspace(-2, 3, 30)).fit(Xtr, ytr),
    "Lasso": LassoCV(cv=5, random_state=0).fit(Xtr, ytr),
}
print(f"n={n} observaciones, p={p} variables, {relevantes} relevantes")
for nombre, m in modelos.items():
    rmse = mean_squared_error(yte, m.predict(Xte)) ** 0.5
    seleccion = np.flatnonzero(np.abs(m.coef_) > 1e-8)
    verdaderas = len(set(seleccion) & set(range(relevantes)))
    print(f"{nombre:6s} RMSE prueba={rmse:.3f} | variables no nulas={len(seleccion):2d} | relevantes recuperadas={verdaderas}/{relevantes}")
print(f"Error irreducible (sigma) = 2.000")
