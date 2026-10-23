"""Level-two signatures for finite piecewise-linear paths; no rough-path lift inference."""

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def signature(path: Array) -> tuple[Array, Array]:
    """Chen recurrence: b <- b + a tensor dx + dx tensor dx / 2."""
    x = np.asarray(path, dtype=float)
    if x.ndim != 2 or len(x) < 1 or x.shape[1] < 1 or not np.isfinite(x).all():
        raise ValueError("Expected finite nonempty (points, dimensions) array")
    a = np.zeros(x.shape[1])
    b = np.zeros((x.shape[1], x.shape[1]))
    for previous, current in zip(x[:-1], x[1:]):
        dx = current - previous
        b += np.outer(a, dx) + 0.5 * np.outer(dx, dx)
        a += dx
    return a, b


def compose(
    left: tuple[Array, Array], right: tuple[Array, Array]
) -> tuple[Array, Array]:
    """Concatenate signatures with matching dimensions."""
    a, b = left
    c, d = right
    if (
        a.ndim != 1
        or c.ndim != 1
        or a.shape != c.shape
        or b.shape != (len(a), len(a))
        or d.shape != b.shape
    ):
        raise ValueError("Signature dimensions differ")
    return a + c, b + d + np.outer(a, c)


def signed_area(path: Array) -> float:
    """Antisymmetric level-two coordinate in two dimensions."""
    _, b = signature(path)
    if b.shape != (2, 2):
        raise ValueError("Area requires two dimensions")
    return float((b[0, 1] - b[1, 0]) / 2)


def polygon_area(path: Array) -> float:
    """Independent shoelace oracle, with closure along endpoint chord."""
    x = np.asarray(path, dtype=float)
    if x.ndim != 2 or x.shape[1] != 2 or len(x) < 1 or not np.isfinite(x).all():
        raise ValueError("Expected finite planar path")
    return float(
        0.5 * np.sum(x[:, 0] * np.roll(x[:, 1], -1) - x[:, 1] * np.roll(x[:, 0], -1))
    )


def circle(n: int, orientation: int = 1, turns: int = 1) -> Array:
    if n < 2 or orientation not in (-1, 1) or turns < 1:
        raise ValueError("Invalid circle parameters")
    t = np.linspace(0, orientation * turns * 2 * np.pi, n + 1)
    x = np.column_stack([np.cos(t), np.sin(t)])
    x[-1] = x[0]
    return x
