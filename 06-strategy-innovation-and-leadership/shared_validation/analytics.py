"""Independent numerical validation utilities for strategic decision models.

The functions here intentionally avoid pandas/numpy to keep numerical assumptions
visible and permit review of small synthetic examples by hand.
"""
from dataclasses import dataclass
from math import isfinite, sqrt
from random import Random
from statistics import mean

@dataclass(frozen=True)
class StressPoint:
    name: str
    parameter: float
    metric: float
    delta_from_base: float

def one_way_sensitivity(model, base_parameters, variable, levels):
    """Change one input at a time; model(params) must return a finite scalar."""
    if variable not in base_parameters or not levels:
        raise ValueError("unknown parameter or empty grid")
    baseline = float(model(dict(base_parameters)))
    if not isfinite(baseline):
        raise ValueError("nonfinite baseline")
    results=[]
    for level in levels:
        if not isfinite(level):
            raise ValueError("nonfinite parameter")
        parameters=dict(base_parameters)
        parameters[variable]=level
        result=float(model(parameters))
        if not isfinite(result):
            raise ValueError("nonfinite scenario metric")
        results.append(StressPoint(variable,float(level),result,result-baseline))
    return {"baseline":baseline,"points":results}

def bootstrap_mean_interval(observations, confidence=.95, resamples=2000, seed=42):
    """Percentile bootstrap interval; independent observations are assumed."""
    values=[float(x) for x in observations]
    if not values or any(not isfinite(x) for x in values):
        raise ValueError("finite observations required")
    if not 0<confidence<1 or not isinstance(resamples,int) or resamples<100:
        raise ValueError("invalid bootstrap configuration")
    rng=Random(seed)
    n=len(values)
    distribution=sorted(mean(values[rng.randrange(n)] for _ in range(n))
                        for _ in range(resamples))
    lower=int((1-confidence)/2*(resamples-1))
    upper=int((1+confidence)/2*(resamples-1))
    return {"estimate":mean(values),"lower":distribution[lower],
            "upper":distribution[upper],"confidence":confidence,
            "resamples":resamples,"seed":seed}

def weighted_scenario_summary(outcomes, probabilities, threshold=0):
    """Scenario expected value, variance and probability below threshold."""
    if not outcomes or len(outcomes)!=len(probabilities):
        raise ValueError("scenario vectors must have matching nonzero lengths")
    if any(not isfinite(float(x)) for x in (*outcomes,*probabilities,threshold)):
        raise ValueError("nonfinite scenario values")
    if any(p<0 for p in probabilities) or abs(sum(probabilities)-1)>1e-10:
        raise ValueError("invalid probabilities")
    expectation=sum(x*p for x,p in zip(outcomes,probabilities))
    variance=sum(p*(x-expectation)**2 for x,p in zip(outcomes,probabilities))
    return {"expected_value":expectation,"standard_deviation":sqrt(variance),
            "downside_probability":sum(p for x,p in zip(outcomes,probabilities)
                                       if x<threshold)}
