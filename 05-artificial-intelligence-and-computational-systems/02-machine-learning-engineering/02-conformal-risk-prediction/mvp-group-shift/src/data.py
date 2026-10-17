import numpy as np

def draw(rng, n, p, multiplier=1.0):
    g = rng.binomial(1, p, n)
    x = rng.normal(size=n)
    sigma = np.where(g == 1, 2.5 * multiplier, 0.5)
    y = 1 + 2*x + 0.5*g + rng.normal(size=n)*sigma
    return np.column_stack([np.ones(n), x, g]), g, y
