import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
productos = {
    # nombre: (PD media, LGD media, EAD media, numero de creditos)
    "consumo": (0.060, 0.65, 5_000, 6000),
    "tarjeta": (0.090, 0.75, 3_000, 5000),
    "vehiculo": (0.030, 0.40, 18_000, 3000),
    "hipotecario": (0.015, 0.20, 90_000, 1500),
}


def beta_con_media(media, kappa, size):
    return rng.beta(media * kappa, (1 - media) * kappa, size)


filas = []
for nombre, (pd_m, lgd_m, ead_m, n) in productos.items():
    pdi = beta_con_media(pd_m, 40, n)
    lgd = beta_con_media(lgd_m, 8, n)
    ead = rng.lognormal(np.log(ead_m), 0.4, n)
    el = pdi * lgd * ead
    # simulacion: incumplimiento ~ Bernoulli(PD), perdida = LGD x EAD si hay default
    perdidas = []
    for _ in range(200):
        d = rng.random(n) < pdi
        perdidas.append((d * lgd * ead).sum())
    filas.append({
        "producto": nombre,
        "exposicion": ead.sum(),
        "EL": el.sum(),
        "EL/exposicion": el.sum() / ead.sum(),
        "perdida_simulada_media": np.mean(perdidas),
    })

tabla = pd.DataFrame(filas).set_index("producto")
tabla["participacion_EL"] = tabla["EL"] / tabla["EL"].sum()
pd.options.display.float_format = "{:,.4f}".format
print(tabla.round(4).to_string())
print(f"EL total = {tabla['EL'].sum():,.0f} sobre exposicion {tabla['exposicion'].sum():,.0f}")
