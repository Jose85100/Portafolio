import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
n = 20000
df = pd.DataFrame({
    "ingreso": rng.lognormal(8.0, 0.5, n),
    "edad": rng.integers(21, 70, n),
    "utilizacion": rng.beta(2, 3, n),
    "mora_previa": rng.poisson(0.4, n),
})
z = (-3.2 - 0.00015 * (df.ingreso - 3000) + 1.8 * df.utilizacion
     + 0.5 * df.mora_previa - 0.01 * (df.edad - 40))
df["default"] = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)

train, test = train_test_split(df, test_size=0.3, random_state=1, stratify=df["default"])


def fit_woe(x, y, bins=5):
    edges = np.unique(np.quantile(x, np.linspace(0, 1, bins + 1)))
    idx = np.digitize(x, edges[1:-1])
    k = len(edges) - 1
    bad = np.array([(y[idx == i] == 1).sum() for i in range(k)]) + 0.5
    good = np.array([(y[idx == i] == 0).sum() for i in range(k)]) + 0.5
    dist_bad, dist_good = bad / bad.sum(), good / good.sum()
    woe = np.log(dist_good / dist_bad)
    iv = float(((dist_good - dist_bad) * woe).sum())
    return edges, woe, iv


def apply_woe(x, edges, woe):
    return woe[np.digitize(x, edges[1:-1])]


features = ["ingreso", "edad", "utilizacion", "mora_previa"]
tables, X_tr, X_te = {}, {}, {}
for f in features:
    edges, woe, iv = fit_woe(train[f].to_numpy(), train["default"].to_numpy())
    tables[f] = (edges, woe, iv)
    X_tr[f] = apply_woe(train[f].to_numpy(), edges, woe)
    X_te[f] = apply_woe(test[f].to_numpy(), edges, woe)

print("Information Value por variable:")
for f in features:
    print(f"  {f:12s} IV = {tables[f][2]:.3f}")

model = LogisticRegression().fit(pd.DataFrame(X_tr), train["default"])
p = model.predict_proba(pd.DataFrame(X_te))[:, 1]
y = test["default"].to_numpy()
auc = roc_auc_score(y, p)
order = np.argsort(p)
cum_bad = np.cumsum(y[order]) / y.sum()
cum_good = np.cumsum(1 - y[order]) / (1 - y).sum()
ks = float(np.max(np.abs(cum_bad - cum_good)))
print(f"Tasa de default en prueba: {y.mean():.3f}")
print(f"AUC = {auc:.3f} | Gini = {2 * auc - 1:.3f} | KS = {ks:.3f}")
