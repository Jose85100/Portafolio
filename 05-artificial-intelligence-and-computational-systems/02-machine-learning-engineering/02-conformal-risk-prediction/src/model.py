"""Split conformal intervals with finite-sample marginal coverage under exchangeability."""
from math import ceil, isfinite

def fit_intervals(y_true, y_pred, alpha=0.1):
    if not 0<alpha<1 or len(y_true)!=len(y_pred) or not y_true: raise ValueError("invalid calibration sample")
    if not all(isfinite(v) for v in [*y_true,*y_pred]): raise ValueError("nonfinite value")
    scores=sorted(abs(a-b) for a,b in zip(y_true,y_pred))
    k=ceil((len(scores)+1)*(1-alpha))
    q=scores[k-1] if k<=len(scores) else float("inf")
    return q

def predict_intervals(predictions, radius):
    if radius<0: raise ValueError("negative radius")
    return [(p-radius,p+radius) for p in predictions]
