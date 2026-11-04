"""Exact moments for competing-risk default time and independent Beta LGD."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

@dataclass(frozen=True)
class Scenario:
    ead_start: float
    ead_end: float
    horizon: float
    hazard_default: float
    hazard_prepay: float
    lgd_alpha: float
    lgd_beta: float

@dataclass(frozen=True)
class LossMoments:
    default_probability: float
    expected_loss: float
    loss_variance: float
    loss_sd: float
    plugin_variance: float
    lgd_mean: float
    lgd_variance: float


def _exp_moment(rate: float, horizon: float, power: int) -> float:
    """Integral_0^T t^power exp(-rate*t) dt, stable for rate=0."""
    if power not in (0, 1, 2):
        raise ValueError("power must be 0, 1, or 2")
    if rate == 0.0:
        return horizon ** (power + 1) / (power + 1)
    x = rate * horizon
    if x < 0.5:
        # Taylor expansion of integral t^k exp(-rate*t) dt; avoid cancellation.
        total = horizon ** (power + 1) / (power + 1)
        term = 1.0
        for n in range(1, 30):
            term *= -x / n
            add = horizon ** (power + 1) * term / (power + n + 1)
            total += add
            if abs(add) <= 1e-16 * abs(total):
                break
        return total
    if power == 0:
        return -math.expm1(-x) / rate
    if power == 1:
        return (1.0 - math.exp(-x) * (1.0 + x)) / rate**2
    return (2.0 - math.exp(-x) * (x*x + 2*x + 2)) / rate**3


def evaluate(s: Scenario) -> LossMoments:
    vals = asdict(s)
    if not all(math.isfinite(v) for v in vals.values()):
        raise ValueError("all inputs must be finite")
    if s.ead_start < 0 or s.ead_end < 0 or s.horizon <= 0:
        raise ValueError("EAD must be nonnegative and horizon positive")
    if s.hazard_default < 0 or s.hazard_prepay < 0 or s.hazard_default + s.hazard_prepay <= 0:
        raise ValueError("hazards must be nonnegative with positive total")
    if s.lgd_alpha <= 0 or s.lgd_beta <= 0:
        raise ValueError("Beta parameters must be positive")
    h = s.hazard_default + s.hazard_prepay
    # EAD(t)=a+b*t; f_default(t)=lambda_d exp(-h*t).
    a = s.ead_start
    b = (s.ead_end - s.ead_start) / s.horizon
    i0, i1, i2 = (_exp_moment(h, s.horizon, k) for k in range(3))
    p_default = s.hazard_default * i0
    ead_first = s.hazard_default * (a*i0 + b*i1)
    ead_second = s.hazard_default * (a*a*i0 + 2*a*b*i1 + b*b*i2)
    lm = s.lgd_alpha / (s.lgd_alpha + s.lgd_beta)
    lm2 = s.lgd_alpha * (s.lgd_alpha + 1) / ((s.lgd_alpha + s.lgd_beta) * (s.lgd_alpha + s.lgd_beta + 1))
    loss_mean = lm * ead_first
    variance = max(0.0, lm2*ead_second - loss_mean**2)
    # Plug-in baseline: replaces uncertain LGD by its mean,
    # retaining default-time uncertainty but dropping LGD parameter variance.
    plugin_var = max(0.0, lm*lm*ead_second - loss_mean**2)
    return LossMoments(p_default, loss_mean, variance, math.sqrt(variance), plugin_var, lm, lm2-lm*lm)


def write_results(s: Scenario, output_dir: Path) -> LossMoments:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate(s)
    (output_dir / "summary.json").write_text(json.dumps({"scenario": asdict(s), "moments": asdict(result), "evidence": "synthetic exact model"}, indent=2) + "\n")
    import csv
    with (output_dir / "comparison.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=["metric","value"], lineterminator="\n"); w.writeheader()
        for key,value in asdict(result).items(): w.writerow({"metric":key,"value":value})
    return result
