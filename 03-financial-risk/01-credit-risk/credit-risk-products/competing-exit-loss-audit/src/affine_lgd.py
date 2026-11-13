"""Exact discounted product of deterministic affine EAD and affine LGD."""
import math
from collections.abc import Sequence
from dataclasses import dataclass

from src.affine import discounted_mean_fraction, project_affine


@dataclass(frozen=True)
class LossPathResult:
    exact_loss: float
    product_of_means_loss: float
    midpoint_product_loss: float
    constant_start_lgd_loss: float
    default_probability: float
    prepayment_probability: float
    survival: float


def second_fraction_moment(x: float) -> float:
    """E[v^2] for density exp(-x*v)/integral_0^1 exp(-x*v)dv, x>=0."""
    if not math.isfinite(x) or x < 0:
        raise ValueError('finite nonnegative hazard-duration required')
    if x < .5:
        # Entire-function series for integrals; avoid subtracting O(1/x^2) terms.
        terms=[(-x)**k / math.factorial(k) for k in range(20)]
        return math.fsum(t/(k+3) for k,t in enumerate(terms))/math.fsum(
            t/(k+1) for k,t in enumerate(terms))
    tail=1/math.expm1(x) if x <= 700 else 0.
    return 2/x/x - (1+2/x)*tail


def project_loss_path(
    durations: Sequence[float],
    default_hazard: Sequence[float],
    prepay_hazard: Sequence[float],
    ead_start: Sequence[float],
    ead_end: Sequence[float],
    lgd_start: Sequence[float],
    lgd_end: Sequence[float],
    discount_forces: Sequence[float],
) -> LossPathResult:
    """Years; annual nonnegative forces; money EAD; LGD endpoints in [0,1].

    EAD and LGD are deterministic conditional-on-survival paths, affine within
    each event interval, possibly discontinuous across intervals. Not expected
    independent random variables; no recovery calibration or causal inference.
    """
    n=len(durations)
    if not 1 <= n <= 360 or any(len(v)!=n for v in (
        default_hazard,prepay_hazard,ead_start,ead_end,lgd_start,lgd_end,discount_forces
    )):
        raise ValueError('matching 1..360 interval vectors required')
    if any(not math.isfinite(v) or not 0<=v<=1 for v in (*lgd_start,*lgd_end)):
        raise ValueError('finite LGD endpoints in [0,1] required')
    # Reuse original validation and exact local default mass with unit EAD/LGD.
    local=[project_affine([dt],[d],[p],[1.],[1.],1.,r) for dt,d,p,r in
           zip(durations,default_hazard,prepay_hazard,discount_forces)]
    if any(not math.isfinite(v) or v<0 for v in (*ead_start,*ead_end)):
        raise ValueError('finite nonnegative EAD endpoints required')
    exact,product_means,midpoint,frozen,defaults,prepays=[],[],[],[],[],[]
    survival=discount=1.
    for dt,d,p,r,e0,e1,l0,l1,item in zip(durations,default_hazard,prepay_hazard,
        discount_forces,ead_start,ead_end,lgd_start,lgd_end,local):
        x=(d+p+r)*dt
        m1=discounted_mean_fraction(x);m2=second_fraction_moment(x)
        # Nonnegative Bernstein weights preserve positivity without signed EAD differences.
        w00=1-2*m1+m2;w01=m1-m2;w11=m2
        expected=(w00*e0*l0 + w01*e0*l1 + w01*e1*l0 + w11*e1*l1)
        weight=survival*discount*item.exact_loss
        mean_e=(1-m1)*e0+m1*e1;mean_l=(1-m1)*l0+m1*l1
        exact.append(weight*expected)
        product_means.append(weight*mean_e*mean_l)
        midpoint.append(weight*(.5*e0+.5*e1)*(.5*l0+.5*l1))
        frozen.append(weight*mean_e*l0)
        defaults.append(survival*item.default_probability)
        prepays.append(survival*item.prepayment_probability)
        survival*=item.survival;discount*=math.exp(-r*dt)
    return LossPathResult(math.fsum(exact),math.fsum(product_means),math.fsum(midpoint),
        math.fsum(frozen),math.fsum(defaults),math.fsum(prepays),survival)
