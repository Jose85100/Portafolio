import numpy as np
from scipy.stats import chi2

rng = np.random.default_rng(23)
vol = np.r_[np.full(700, 0.008), np.full(150, 0.025), np.full(400, 0.009)]
r = rng.standard_normal(len(vol)) * vol
ventana, nivel = 250, 0.99

excepciones = []
for t in range(ventana, len(r)):
    var = -np.quantile(r[t - ventana:t], 1 - nivel)
    excepciones.append(int(r[t] < -var))
x = np.array(excepciones)
n, k = len(x), int(x.sum())
p = 1 - nivel


def log_l(pi, n, k):
    pi = min(max(pi, 1e-12), 1 - 1e-12)
    return (n - k) * np.log(1 - pi) + k * np.log(pi)


lr_pof = -2 * (log_l(p, n, k) - log_l(k / n, n, k))
n00 = n01 = n10 = n11 = 0
for a, b in zip(x[:-1], x[1:]):
    n00 += (a == 0 and b == 0)
    n01 += (a == 0 and b == 1)
    n10 += (a == 1 and b == 0)
    n11 += (a == 1 and b == 1)
pi01 = n01 / max(n00 + n01, 1)
pi11 = n11 / max(n10 + n11, 1)
pi = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)


def ll(pi_, a, b):
    pi_ = min(max(pi_, 1e-12), 1 - 1e-12)
    return a * np.log(1 - pi_) + b * np.log(pi_)


lr_ind = -2 * (ll(pi, n00 + n10, n01 + n11) - (ll(pi01, n00, n01) + ll(pi11, n10, n11)))
print(f"Observaciones: {n} | excepciones: {k} | esperadas: {n * p:.1f} | tasa observada: {k / n:.4f}")
print(f"Kupiec (cobertura):      LR={lr_pof:6.2f}  p-valor={1 - chi2.cdf(lr_pof, 1):.4f}")
print(f"Christoffersen (indep.): LR={lr_ind:6.2f}  p-valor={1 - chi2.cdf(lr_ind, 1):.4f}")
print(f"Excepciones consecutivas (n11): {n11}")
