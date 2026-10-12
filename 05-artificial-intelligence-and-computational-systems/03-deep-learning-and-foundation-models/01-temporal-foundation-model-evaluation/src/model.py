"""Leakage-safe expanding-window evaluation; a baseline for foundation models."""
from math import sqrt

def rolling_origin(series, horizon=1, min_train=5, predictor=None):
    if horizon<1 or min_train<2 or len(series)<min_train+horizon: raise ValueError("insufficient observations")
    predictor=predictor or (lambda history: history[-1])
    rows=[]
    for end in range(min_train,len(series)-horizon+1):
        forecast=predictor(tuple(series[:end]))
        actual=series[end+horizon-1]
        rows.append({"origin":end-1,"forecast":forecast,"actual":actual,"error":actual-forecast})
    return {"rmse":sqrt(sum(r["error"]**2 for r in rows)/len(rows)),"rows":rows}
