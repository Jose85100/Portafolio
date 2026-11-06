"""Observed individual-default benchmark using UCI Taiwan credit cards (dataset 350).

Educational external benchmark only. Outcome is next-month default, NOT Colombian
12-month IFRS 9 PD. Random stratified holdout is not out-of-time validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def benchmark(output: str, seed: int = 42) -> dict:
    from ucimlrepo import fetch_ucirepo
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, brier_score_loss, roc_curve
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    dataset = fetch_ucirepo(id=350)
    X = dataset.data.features.copy()
    y = dataset.data.targets.iloc[:, 0].astype(int)
    if len(X) != 30000 or len(y) != len(X):
        raise ValueError("Unexpected row count; revalidate dataset revision")
    if set(y.unique()) != {0, 1}:
        raise ValueError("Target must be binary")
    # Exclude sensitive/demographic variables and use cash-flow & behavior only.
    exclude = {"SEX", "EDUCATION", "MARRIAGE", "AGE", "X2", "X3", "X4", "X5"}
    columns = [str(c) for c in X.columns if str(c).upper() not in exclude]
    if not columns:
        raise ValueError("No predictors left")
    X = X.loc[:, columns]
    # A stratified random split is an illustrative benchmark, not temporal validation.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.25, random_state=seed)
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                          LogisticRegression(max_iter=2000, random_state=seed))
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, probabilities))
    fpr, tpr, _ = roc_curve(y_test, probabilities)
    result = {
        "dataset": "UCI 350 Default of Credit Card Clients",
        "doi": "10.24432/C55S3H",
        "license": "CC BY 4.0",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "observed_rows": len(y), "train_rows": len(y_train), "test_rows": len(y_test),
        "target": "default payment next month (Taiwan, 2005)",
        "not_target": "Colombian PD12m or IFRS9 lifetime ECL",
        "split": "random_stratified_NOT_OOT",
        "model": "median-imputed standardized logistic regression",
        "seed": seed,
        "features": columns,
        "feature_count": len(columns),
        "test_default_rate": float(y_test.mean()),
        "test_auc": auc, "test_gini": 2 * auc - 1,
        "test_ks": float(np.max(tpr - fpr)),
        "test_brier": float(brier_score_loss(y_test, probabilities)),
        "limitation": "No Colombian representativeness, no population PD calibration, no independent OOT sample",
    }
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=True)
    # Save measurements, not individuals, credentials or identifiable input data.
    serialized = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    (folder / "uci_pd_benchmark.json").write_text(serialized, encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.output, args.seed), indent=2))
