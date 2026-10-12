from dataclasses import dataclass
from math import isfinite
from typing import Sequence

@dataclass(frozen=True)
class Exposure:
    pd: float
    lgd: float
    ead: float

def expected_loss(exposures: Sequence[Exposure]) -> float:
    for e in exposures:
        if not (isfinite(e.pd) and isfinite(e.lgd) and isfinite(e.ead) and 0 <= e.pd <= 1 and 0 <= e.lgd <= 1 and e.ead >= 0):
            raise ValueError("invalid exposure")
    return sum(e.pd * e.lgd * e.ead for e in exposures)

def independent_variance(exposures: Sequence[Exposure]) -> float:
    expected_loss(exposures)
    return sum((e.lgd * e.ead)**2 * e.pd * (1 - e.pd) for e in exposures)
