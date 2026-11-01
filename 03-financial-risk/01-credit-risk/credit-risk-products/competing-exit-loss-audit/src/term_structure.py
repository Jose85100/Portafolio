"""Event-aligned deterministic exposure and piecewise discount forces."""
import math
from collections.abc import Sequence
from dataclasses import dataclass

from src.affine import project_affine


@dataclass(frozen=True)
class TermResult:
    exact_loss: float
    midpoint_exposure_loss: float
    default_probability: float
    prepayment_probability: float
    survival: float
    terminal_discount: float


def project_term_structure(
    durations: Sequence[float],
    default_hazard: Sequence[float],
    prepay_hazard: Sequence[float],
    ead_start: Sequence[float],
    ead_end: Sequence[float],
    discount_forces: Sequence[float],
    lgd: float = 0.45,
) -> TermResult:
    """Years; cause-specific hazards/discount forces year^-1; EAD monetary.

    Each interval is affine conditional EAD; adjacent endpoints may jump.
    Scheduled payment reduces next interval's EAD, not current interval's slope.
    Nonnegative forces only. No event-time default atoms; payment/default ties
    have zero probability under these absolutely continuous hazards.
    """
    n = len(durations)
    if not 1 <= n <= 360 or any(len(v) != n for v in (
        default_hazard, prepay_hazard, ead_start, ead_end, discount_forces
    )):
        raise ValueError("matching 1..360 interval vectors required")
    # Validate every interval before aggregation, including zero-survival tails.
    local = [project_affine([dt],[d],[p],[start],[end],lgd,r) for
             dt,d,p,start,end,r in zip(durations,default_hazard,prepay_hazard,
                                     ead_start,ead_end,discount_forces)]
    loss, midpoint, defaults, prepays = [], [], [], []
    survival, discount = 1.0, 1.0
    for dt,r,item in zip(durations,discount_forces,local):
        loss.append(survival * discount * item.exact_loss)
        midpoint.append(survival * discount * item.midpoint_loss)
        defaults.append(survival * item.default_probability)
        prepays.append(survival * item.prepayment_probability)
        survival *= item.survival
        discount *= math.exp(-r*dt)
    return TermResult(math.fsum(loss),math.fsum(midpoint),math.fsum(defaults),
                      math.fsum(prepays),survival,discount)
