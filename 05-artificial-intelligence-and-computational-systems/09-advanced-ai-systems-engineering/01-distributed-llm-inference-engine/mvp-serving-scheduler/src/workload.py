"""Deterministic synthetic arrivals and request lengths; no user data."""
from __future__ import annotations
import random
from .simulator import Request

def generate(seed: int, regime: str, n: int = 90) -> list[Request]:
    if n < 1:
        raise ValueError("n must be positive")
    if regime not in ("light", "bursty", "long_prompts"):
        raise ValueError("unknown regime")
    rng = random.Random(seed)
    now = 0.0
    requests = []
    for i in range(n):
        rate = {"light": .065, "bursty": .38, "long_prompts": .20}[regime]
        now += rng.expovariate(rate)
        if regime == "bursty" and i % 30 == 0:
            now += 10.0
        prompt = rng.randint(32, 144) if regime != "long_prompts" else rng.randint(384, 840)
        output = rng.randint(8, 44)
        requests.append(Request(i, now, prompt, output))
    return requests
