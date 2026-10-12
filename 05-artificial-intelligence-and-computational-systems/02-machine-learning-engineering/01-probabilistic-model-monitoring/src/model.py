"""Beta-Binomial monitoring of observed binary error rates."""
from math import sqrt

def monitor(reference_errors, current_errors, alpha=1.0, beta=1.0, threshold=0.05):
    if alpha <= 0 or beta <= 0 or not 0 <= threshold <= 1: raise ValueError("invalid prior or threshold")
    for values in (reference_errors, current_errors):
        if not values or any(v not in (0, 1) for v in values): raise ValueError("nonempty binary labels required")
    def posterior(x):
        a, b = alpha + sum(x), beta + len(x) - sum(x)
        return a/(a+b), a*b/((a+b)**2*(a+b+1))
    baseline, v0 = posterior(reference_errors)
    recent, v1 = posterior(current_errors)
    delta = recent - baseline
    z = delta/sqrt(v0+v1)
    return {"reference_rate":baseline,"current_rate":recent,"delta":delta,"z_score":z,"alert":delta>threshold and z>1.645}
