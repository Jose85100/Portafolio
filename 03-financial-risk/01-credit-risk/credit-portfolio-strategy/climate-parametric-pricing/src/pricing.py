"""Pricing primitives for climate-index insurance experiments (synthetic research only)."""
from __future__ import annotations
import numpy as np

def payout(index, trigger: float, exhaustion: float, limit: float):
    """Linear capped payout for a low-tail hazard index such as rainfall."""
    if not np.isfinite(trigger+exhaustion+limit) or exhaustion >= trigger or limit < 0:
        raise ValueError("finite parameters, exhaustion < trigger, and limit >= 0 required")
    x=np.asarray(index,dtype=float)
    if not np.all(np.isfinite(x)): raise ValueError("index must be finite")
    z=limit*np.clip((trigger-x)/(trigger-exhaustion),0.,1.)
    return float(z) if z.ndim==0 else z

def pure_premium(payments, weights=None) -> float:
    z=np.asarray(payments,dtype=float)
    if z.size==0 or not np.all(np.isfinite(z)) or np.any(z<0):
        raise ValueError("payments must be finite, non-empty, and non-negative")
    if weights is None: return float(z.mean())
    w=np.asarray(weights,dtype=float)
    if w.shape!=z.shape or not np.all(np.isfinite(w)) or np.any(w<0) or w.sum()<=0:
        raise ValueError("weights must match payments and have positive sum")
    return float((w/w.sum())@z)

def tvar(payments, alpha: float=.95) -> float:
    z=np.asarray(payments,dtype=float)
    if z.size==0 or not np.all(np.isfinite(z)) or np.any(z<0) or not 0<alpha<1:
        raise ValueError("valid non-negative payments and 0 < alpha < 1 required")
    q=np.quantile(z,alpha)
    return float(z[z>=q].mean())

def technical_premium(payments, tail_loading=0., alpha=.95, expense=0., reinsurance=0., capital=0.):
    """Illustrative premium; each loading is explicit and non-negative."""
    c=np.asarray([tail_loading,expense,reinsurance,capital],dtype=float)
    if not np.all(np.isfinite(c)) or np.any(c<0): raise ValueError("loadings must be non-negative")
    mean=pure_premium(payments)
    return float(mean+tail_loading*max(tvar(payments,alpha)-mean,0)+expense+reinsurance+capital)
