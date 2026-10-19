"""Falsification-oriented economics experiments; synthetic DGPs only.

Each experiment has a valid-assumption case and a deliberately broken case.
All results are numerical diagnostics, never empirical causal conclusions.
"""
from math import exp, sqrt
from random import Random


def did_estimate(treated_pre, treated_post, control_pre, control_post):
    """Two-group, two-period difference-in-differences in levels."""
    return (treated_post-treated_pre)-(control_post-control_pre)


def did_counterexample(n=500, treatment=2.0, differential_trend=0.0, seed=42):
    """Potential outcomes: untreated treated-group trend differs by differential_trend.

    Baseline levels vary by group; randomized noise averages out asymptotically.
    The ATT is treatment, but DiD converges to treatment + differential_trend.
    """
    if n < 2: raise ValueError("n must be >=2")
    rng=Random(seed)
    tp,tpost,cp,cpost=[],[],[],[]
    for _ in range(n):
        baseline=rng.gauss(0,1)
        tp.append(2+baseline+rng.gauss(0,.5))
        tpost.append(3+baseline+treatment+differential_trend+rng.gauss(0,.5))
        cp.append(baseline+rng.gauss(0,.5))
        cpost.append(1+baseline+rng.gauss(0,.5))
    avg=lambda a:sum(a)/len(a)
    return {"estimate":did_estimate(avg(tp),avg(tpost),avg(cp),avg(cpost)),
            "true_att":treatment,"differential_trend":differential_trend}


def phillips_slope(gap, inflation):
    """OLS slope with intercept: association, not a structural NKPC parameter."""
    if len(gap)!=len(inflation) or len(gap)<3:raise ValueError("invalid sample")
    mx=sum(gap)/len(gap);my=sum(inflation)/len(inflation)
    den=sum((x-mx)**2 for x in gap)
    if den<=1e-12:raise ValueError("no gap variation")
    return sum((x-mx)*(y-my) for x,y in zip(gap,inflation))/den


def phillips_policy_counterexample(n=10000, structural_kappa=.3, feedback=0.0, seed=42):
    """Simultaneous system: pi=kappa*x+u; x=v-feedback*u.

    Expectations are held fixed at zero; this is NOT a full New Keynesian model.
    Cov(x,u)=-feedback, Var(x)=1+feedback**2. OLS plim =
    kappa-feedback/(1+feedback**2). Policy feedback can reverse the slope.
    """
    if n<3:raise ValueError("n must be >=3")
    rng=Random(seed);xs=[];ys=[]
    for _ in range(n):
        u=rng.gauss(0,1);v=rng.gauss(0,1)
        x=v-feedback*u
        xs.append(x);ys.append(structural_kappa*x+u)
    return {"estimate":phillips_slope(xs,ys),
            "structural_kappa":structural_kappa,
            "population_ols":structural_kappa-feedback/(1+feedback**2)}


def expected_loss(pd, lgd, ead):
    """Conditional expectation of credit losses under fixed PD, LGD and EAD."""
    if not(len(pd)==len(lgd)==len(ead)) or not pd:raise ValueError("aligned inputs required")
    if any(not(0<=p<=1 and 0<=l<=1 and e>=0) for p,l,e in zip(pd,lgd,ead)):
        raise ValueError("invalid risk parameters")
    return sum(p*l*e for p,l,e in zip(pd,lgd,ead))


def portfolio_loss_tail(n=20000, common_factor_loading=0.0, seed=42):
    """Two obligors: Bernoulli default with conditional PD via Gaussian one-factor.

    Z_i=sqrt(rho)*F+sqrt(1-rho)*eps_i, default when Z_i<Phi^-1(.1).
    Marginal PD stays .1; expected loss stays 20 (2x100x.1);
    tail risk changes with rho. Returns P(both default) and empirical VaR95.
    """
    from statistics import NormalDist
    if n<2 or not 0<=common_factor_loading<1:raise ValueError("invalid scenario")
    rng=Random(seed);normal=NormalDist();threshold=normal.inv_cdf(.1)
    rho=common_factor_loading;losses=[];joint=0
    for _ in range(n):
        f=rng.gauss(0,1)
        defaults=[sqrt(rho)*f+sqrt(1-rho)*rng.gauss(0,1)<threshold for _ in range(2)]
        joint+=int(all(defaults))
        losses.append(100*sum(defaults))
    losses.sort()
    return {"mean_loss":sum(losses)/n,"joint_default_probability":joint/n,
            "var95":losses[int(.95*n)-1],"analytical_el":20.0}
