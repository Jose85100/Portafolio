import numpy as np
from scipy import stats

rng = np.random.default_rng(17)
gl = 4
retornos = stats.t.rvs(gl, size=2500, random_state=rng) * 0.01 / np.sqrt(gl / (gl - 2))
valor = 1_000_000


def historico(r, nivel):
    var = -np.quantile(r, 1 - nivel)
    es = -r[r <= -var].mean()
    return var, es


def normal(r, nivel):
    mu, sd = r.mean(), r.std(ddof=1)
    z = stats.norm.ppf(1 - nivel)
    var = -(mu + sd * z)
    es = -(mu - sd * stats.norm.pdf(z) / (1 - nivel))
    return var, es


def t_student(r, nivel):
    df, loc, escala = stats.t.fit(r)
    sim = stats.t.rvs(df, loc, escala, size=400_000, random_state=rng)
    return historico(sim, nivel)


print(f"Valor del portafolio: {valor:,.0f} | observaciones: {len(retornos)}")
print(f"{'nivel':>6} {'metodo':>12} {'VaR':>12} {'ES':>12}")
for nivel in (0.95, 0.99):
    for nombre, f in (("historico", historico), ("normal", normal), ("t-student", t_student)):
        var, es = f(retornos, nivel)
        print(f"{nivel:>6.2f} {nombre:>12} {var * valor:>12,.0f} {es * valor:>12,.0f}")
