"""Independent merge oracle; PYTHONPATH points to streaming-moments."""
import math
import random
from decimal import Decimal, localcontext
from src.dynamic import DynamicMoments

rng = random.Random(1101)
worst = (0.0, -1)
for case in range(1000):
    xs = [math.ldexp(rng.uniform(-1, 1), rng.randint(-1070, 1020))
          for _ in range(rng.randint(2, 50))]
    cut = rng.randint(0, len(xs))
    states = []
    for chunk in (xs[:cut], xs[cut:]):
        state = DynamicMoments()
        for value in chunk:
            state = state.push(value)
        states.append(state)
    merged = states[0].merge(states[1])
    assert merged.state.n == len(xs)
    with localcontext() as context:
        context.prec = 100
        values = list(map(Decimal, xs))
        mean = sum(values) / len(values)
        expected = float((sum((x-mean)**2 for x in values) / len(values)).sqrt())
    actual = merged.result().std
    assert actual is not None
    error = abs(actual-expected)/expected if expected else abs(actual-expected)
    worst = max(worst, (error, case))
assert worst[0] < 1e-12, worst
print(f'1000 mixed-scale disjoint merges; max relative SD error={worst[0]:.17g}; case={worst[1]}')
