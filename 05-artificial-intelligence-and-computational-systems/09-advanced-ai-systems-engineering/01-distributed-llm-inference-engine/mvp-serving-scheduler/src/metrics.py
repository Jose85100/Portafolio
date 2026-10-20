"""Metrics computed from simulated timestamps, with explicit empty-set behavior."""
from __future__ import annotations
import math
from .simulator import Run, Config

def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    v = sorted(values)
    index = (len(v) - 1) * q
    lo = int(index)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (index - lo)

def summarize(run: Run, cfg: Config) -> dict[str, float]:
    if not run.completions:
        return {"requests": 0.0, "median_ttft_ms": math.nan, "p99_tpot_ms": math.nan,
                "p95_e2e_ms": math.nan, "throughput_tok_s": 0.0, "goodput_req_s": 0.0,
                "slo_fraction": math.nan, "peak_kv_tokens": 0.0, "iterations": 0.0}
    ttfts = [c.ttft_ms for c in run.completions]
    tpots = [x for c in run.completions for x in c.tpots_ms]
    e2e = [c.finish_ms - c.arrival_ms for c in run.completions]
    ok = [c for c in run.completions if c.ttft_ms <= cfg.ttft_slo_ms
          and all(v <= cfg.tpot_slo_ms for v in c.tpots_ms)]
    span = run.finish_ms - min(c.arrival_ms for c in run.completions)
    return {"requests": float(len(run.completions)),
            "median_ttft_ms": percentile(ttfts, .5),
            "p99_tpot_ms": percentile(tpots, .99),
            "p95_e2e_ms": percentile(e2e, .95),
            "throughput_tok_s": sum(len(c.token_times) for c in run.completions) * 1000 / span,
            "goodput_req_s": len(ok) * 1000 / span,
            "slo_fraction": len(ok) / len(run.completions),
            "peak_kv_tokens": float(run.peak_reserved_tokens),
            "iterations": float(run.iterations)}
