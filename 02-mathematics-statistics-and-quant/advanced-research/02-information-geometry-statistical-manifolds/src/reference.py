"""Independent high-precision angle formula, not the chord formula replay."""

import mpmath as mp
from src.geometry import Array, pair


def oracle_fr(p: Array, q: Array) -> float:
    a, b = pair(p, q)
    with mp.workdps(80):
        aa = [mp.mpf(float(v)) for v in a]
        bb = [mp.mpf(float(v)) for v in b]
        aa = [v / mp.fsum(aa) for v in aa]
        bb = [v / mp.fsum(bb) for v in bb]
        affinity = mp.fsum(mp.sqrt(u * v) for u, v in zip(aa, bb, strict=True))
        return float(2 * mp.acos(min(mp.mpf(1), max(mp.mpf(0), affinity))))
