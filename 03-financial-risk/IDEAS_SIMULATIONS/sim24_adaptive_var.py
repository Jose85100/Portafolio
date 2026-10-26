"""Idea 2.4: VaR con cobertura adaptativa (ACI, Gibbs & Candes 2021) vs VaR estatico,
con cambio de regimen de volatilidad (sigma 1 -> 2 en t=500, N=1000). Semilla fija."""
import numpy as np
from scipy import stats
rng = np.random.default_rng(2424)
T, t_break, W, alpha, gamma, R = 1000, 500, 250, 0.05, 0.01, 500

def simulate_path(r):
    sig = np.where(np.arange(T) < t_break, 1.0, 2.0)
    return sig * rng.standard_normal(T)     # perdidas (signo: L>VaR es excepcion)

def var_path(L, adaptive):
    a_t = alpha
    exc = np.zeros(T, dtype=bool)
    for t in range(W, T):
        hist = L[t-W:t]
        sig_hat = np.sqrt(np.mean(hist**2))           # pronostico de volatilidad (ventana 250)
        zq = stats.norm.ppf(1 - a_t)
        var_t = zq * sig_hat
        exc[t] = L[t] > var_t
        if adaptive:                                   # ACI: alpha_{t+1} = alpha_t + gamma (alpha - err_t)
            a_t = np.clip(a_t + gamma * (alpha - exc[t]), 1e-4, 0.5)
    return exc

res = {"estatico": [], "adaptativo": []}
for r in range(R):
    L = simulate_path(r)
    res["estatico"].append(var_path(L, False)[W:])
    res["adaptativo"].append(var_path(L, True)[W:])

brk = t_break - W
for name in res:
    E = np.array(res[name])
    pre = E[:, :brk].mean(); post = E[:, brk:].mean(); tot = E.mean()
    # maximo de excepciones consecutivas (clusters) por replica
    def max_run(x):
        m = c = 0
        for v in x:
            c = c + 1 if v else 0; m = max(m, c)
        return m
    mr = np.mean([max_run(e) for e in E])
    print(f"{name:12s} tasa total={tot:.4f}  pre-quiebre={pre:.4f}  post-quiebre={post:.4f}  racha max media={mr:.2f}")
print("Objetivo alpha =", alpha)
