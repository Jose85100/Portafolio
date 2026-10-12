"""Leakage-aware daily price features and forward targets."""
import csv
import datetime as dt
import math
from collections import defaultdict

def build_features(path, lookback=3, horizon=1):
    if lookback < 1 or horizon < 1:
        raise ValueError("positive lookback and horizon required")
    groups = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not {"asset", "date", "price"}.issubset(reader.fieldnames or []):
            raise ValueError("missing columns")
        for row in reader:
            price = float(row["price"])
            if not math.isfinite(price) or price <= 0:
                raise ValueError("invalid price")
            groups[row["asset"]].append((dt.date.fromisoformat(row["date"]), price))
    output = []
    for asset, series in sorted(groups.items()):
        series.sort()
        if len({d for d, _ in series}) != len(series):
            raise ValueError("duplicate asset/date")
        for i in range(lookback, len(series)-horizon):
            date, price = series[i]
            past = series[i-lookback][1]
            future = series[i+horizon][1]
            output.append({"asset": asset, "feature_date": date.isoformat(),
                           "momentum": price/past-1, "target_end": series[i+horizon][0].isoformat(),
                           "forward_return": future/price-1})
    return output

def temporal_split(records, train_end, test_start):
    """Purge train labels overlapping test; preserve time order."""
    dt.date.fromisoformat(train_end)
    dt.date.fromisoformat(test_start)
    if train_end >= test_start:
        raise ValueError("test_start must follow train_end")
    train = [r for r in records if r["feature_date"] <= train_end and r["target_end"] < test_start]
    test = [r for r in records if r["feature_date"] >= test_start]
    return train, test
