"""Independent mixed-scale Decimal oracle. Run with PYTHONPATH=PROJECT."""
import math
import random
from decimal import Decimal, localcontext
from src.dynamic import dynamic_moments

rng = random.Random(31)
worst = (0.0, -1)
for case in range(1000):
    xs = [math.ldexp(rng.uniform(-1, 1), rng.randint(-1070, 1020))
          for _ in range(rng.randint(2, 30))]
    with localcontext() as context:
        context.prec = 100
        values = list(map(Decimal, xs))
        mean = sum(values) / len(values)
        reference = float((sum((x - mean) ** 2 for x in values) / len(values)).sqrt())
    actual = dynamic_moments(xs).std
    assert actual is not None
    error = abs(actual - reference) / reference if reference else abs(actual - reference)
    worst = max(worst, (error, case))
assert worst[0] < 1e-12, worst
print(f"1000 mixed-scale cases; max relative SD error={worst[0]:.17g}; case={worst[1]}")
