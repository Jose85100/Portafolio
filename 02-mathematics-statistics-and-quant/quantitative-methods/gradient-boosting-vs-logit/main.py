import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(59)
n = 30000
X = rng.standard_normal((n, 6))
casos = {
    "lineal": X[:, 0] * 1.0 + X[:, 1] * 0.7 - X[:, 2] * 0.5 - 1.0,
    "no_lineal": np.sin(2 * X[:, 0]) + X[:, 1] * X[:, 2] + (X[:, 3] > 0.5) * 1.2 - 1.0,
}
print(f"{'caso':>10} {'modelo':>10} {'AUC':>7} {'Brier':>7}")
for caso, z in casos.items():
    y = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    for nombre, m in (("logit", LogisticRegression(max_iter=1000)),
                      ("boosting", HistGradientBoostingClassifier(random_state=0))):
        p = m.fit(Xtr, ytr).predict_proba(Xte)[:, 1]
        print(f"{caso:>10} {nombre:>10} {roc_auc_score(yte, p):>7.3f} {brier_score_loss(yte, p):>7.3f}")
