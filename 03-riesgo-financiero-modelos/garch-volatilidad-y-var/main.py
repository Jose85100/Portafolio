import numpy as np
from arch import arch_model
from scipy import stats

rng = np.random.default_rng(29)
n = 3000
omega, alpha, beta, gl = 0.02, 0.08, 0.90, 6
r = np.zeros(n)
h = np.zeros(n)
h[0] = omega / (1 - alpha - beta)
escala_t = np.sqrt((gl - 2) / gl)
for t in range(1, n):
    h[t] = omega + alpha * r[t - 1] ** 2 + beta * h[t - 1]
    r[t] = np.sqrt(h[t]) * stats.t.rvs(gl, random_state=rng) * escala_t

modelo = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1, dist="t")
res = modelo.fit(disp="off")
p = res.params
print("Parametros (estimado vs verdadero):")
print(f"  omega: {p['omega']:.3f} vs {omega}")
print(f"  alpha: {p['alpha[1]']:.3f} vs {alpha}")
print(f"  beta:  {p['beta[1]']:.3f} vs {beta}")
print(f"  gl:    {p['nu']:.1f} vs {gl}")
pron = res.forecast(horizon=1)
sigma = np.sqrt(pron.variance.values[-1, 0])
nu = p["nu"]
z = stats.t.ppf(0.01, nu) * np.sqrt((nu - 2) / nu)
var99 = -(p["mu"] + sigma * z)
print(f"Volatilidad pronosticada a 1 dia: {sigma:.3f}% | VaR 99% a 1 dia: {var99:.3f}%")
