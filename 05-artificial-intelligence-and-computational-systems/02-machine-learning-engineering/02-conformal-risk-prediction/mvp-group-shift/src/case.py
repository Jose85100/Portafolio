import numpy as np
from .data import draw
from .calibration import fit

def case(seed, regime):
    rng = np.random.default_rng(seed)
    p = .04 if regime == "rare_group" else .25
    test_p = .25 if regime == "stable" else .80
    xtr, _, ytr = draw(rng, 400, p)
    xc, gc, yc = draw(rng, 400, p)
    xt, gt, yt = draw(rng, 800, test_p, 1.7 if regime == "conditional_shift" else 1.)
    beta = np.linalg.lstsq(xtr, ytr, rcond=None)[0]
    global_q, groups = fit(yc-xc@beta, gc)
    if np.sum(gc == 1) < 25:
        groups.pop(1, None)
    return yt-xt@beta, gt, global_q, groups
