"""Idea 2.1: poder del test Z2 de Acerbi-Szekely frente a Kupiec (VaR) con N=250, alpha=0.025.
Pronosticos constantes: VaR y ES de una N(0,1). Semilla fija."""
import numpy as np
from scipy import stats
rng = np.random.default_rng(2026)
N, alpha, R = 250, 0.025, 20000
z = stats.norm.ppf(1 - alpha)
VaR = z                                   # cuantil de perdida
ES = stats.norm.pdf(z) / alpha            # ES normal = phi(z)/alpha

def stats_for(L):
    # L: (R, N) perdidas. Exceso I = 1{L > VaR}
    I = L > VaR
    x = I.sum(axis=1)
    # Kupiec POF
    phat = x / N
    with np.errstate(divide="ignore", invalid="ignore"):
        ll0 = (N - x) * np.log(1 - alpha) + x * np.log(alpha)
        ll1 = np.where(x > 0, (N - x) * np.log(1 - phat) + x * np.log(phat), (N - x) * np.log(1 - 0.0))
        lr = -2 * (ll0 - ll1)
    lr = np.nan_to_num(lr, nan=0.0, posinf=1e9)
    # Z2 (Acerbi-Szekely): Z2 = 1 - (1/(N alpha)) sum I_t L_t / ES_t ; E[Z2]=0 bajo H0
    z2 = 1 - (I * L / ES).sum(axis=1) / (N * alpha)
    return lr, z2

def simulate(draw):
    L = draw((R, N))
    return stats_for(L)

# Null: L ~ N(0,1) (modelo correcto)
lr0, z20 = simulate(lambda s: rng.standard_normal(s))
crit_kup = np.quantile(lr0, 0.95)          # valor critico exacto por simulacion (tamano 5 %)
crit_z2 = np.quantile(z20, 0.05)           # rechazar si Z2 cae por debajo del 5 %
print("Criticos simulados: Kupiec=%.3f Z2=%.3f" % (crit_kup, crit_z2))
print(f"Tamano empirico 5 %: Kupiec={np.mean(lr0>crit_kup):.3f}  Z2={np.mean(z20<crit_z2):.3f}")

def t_scaled(nu):
    def f(s):
        return rng.standard_t(nu, size=s) * np.sqrt((nu - 2) / nu)  # varianza 1
    return f

alts = {
  "t(4) misma varianza (colas pesadas)": t_scaled(4),
  "t(6) misma varianza": t_scaled(6),
  "N(0,1.2^2) (volatilidad subestimada)": lambda s: 1.2 * rng.standard_normal(s),
  "N(0,1.1^2)": lambda s: 1.1 * rng.standard_normal(s),
}
print(f"{'Alternativa':42s} {'Kupiec':>8s} {'Z2':>8s}")
for name, draw in alts.items():
    lr, z2 = simulate(draw)
    print(f"{name:42s} {np.mean(lr>crit_kup):8.3f} {np.mean(z2<crit_z2):8.3f}")
print("Nota: ES teorico normal =", round(ES,4), " VaR =", round(VaR,4))
