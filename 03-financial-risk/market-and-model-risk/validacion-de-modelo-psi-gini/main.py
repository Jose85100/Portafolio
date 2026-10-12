import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(37)


def generar(n, desplazamiento):
    x1 = rng.normal(0 + desplazamiento, 1, n)
    x2 = rng.normal(0, 1, n)
    x3 = rng.normal(0, 1, n)
    z = -2.5 + 0.9 * x1 + 0.6 * x2 + 0.5 * x1 * x3
    y = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return pd.DataFrame({"x1": x1, "x2": x2, "x3": x3}), y


Xd, yd = generar(20000, 0.0)
Xo, yo = generar(8000, 0.5)  # fuera de tiempo con desplazamiento en x1

champion = LogisticRegression().fit(Xd, yd)
challenger = HistGradientBoostingClassifier(random_state=0).fit(Xd, yd)


def psi(esperado, actual, bins=10):
    cortes = np.quantile(esperado, np.linspace(0, 1, bins + 1))
    cortes[0], cortes[-1] = -np.inf, np.inf
    e = np.histogram(esperado, cortes)[0] / len(esperado)
    a = np.histogram(actual, cortes)[0] / len(actual)
    e, a = np.clip(e, 1e-4, None), np.clip(a, 1e-4, None)
    return float(((a - e) * np.log(a / e)).sum())


for nombre, m in (("champion (logit)", champion), ("challenger (GBM)", challenger)):
    pd_d = m.predict_proba(Xd)[:, 1]
    pd_o = m.predict_proba(Xo)[:, 1]
    gini_d, gini_o = 2 * roc_auc_score(yd, pd_d) - 1, 2 * roc_auc_score(yo, pd_o) - 1
    p = psi(pd_d, pd_o)
    alerta = "ROJO" if p > 0.25 else "AMBAR" if p > 0.10 else "VERDE"
    print(f"{nombre}: Gini desarrollo={gini_d:.3f} OOT={gini_o:.3f} | PSI score={p:.3f} [{alerta}]")

pd_o = champion.predict_proba(Xo)[:, 1]
tabla = pd.DataFrame({"pd": pd_o, "y": yo})
tabla["decil"] = pd.qcut(tabla["pd"], 5, labels=False)
cal = tabla.groupby("decil").agg(pd_media=("pd", "mean"), tasa_observada=("y", "mean"))
print("Calibracion del champion en OOT (por quintil):")
print(cal.round(4).to_string())
print(f"PD media predicha {tabla['pd'].mean():.4f} vs tasa observada {tabla['y'].mean():.4f}")
