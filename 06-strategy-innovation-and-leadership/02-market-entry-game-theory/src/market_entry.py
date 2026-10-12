"""Exact analysis of finite 2x2 normal-form games."""
from math import isfinite

def _validate(payoffs):
    if len(payoffs) != 2 or any(len(row) != 2 for row in payoffs):
        raise ValueError("expected a 2x2 payoff matrix")
    if not all(isinstance(cell, (tuple, list)) and len(cell) == 2 and
               all(isfinite(float(x)) for x in cell)
               for row in payoffs for cell in row):
        raise ValueError("each cell needs two finite payoffs")

def pure_nash(payoffs, tolerance=1e-12):
    """Return action pairs (row_player, column_player)."""
    _validate(payoffs)
    equilibria = []
    for i in range(2):
        for j in range(2):
            a, b = payoffs[i][j]
            if a >= payoffs[1-i][j][0]-tolerance and b >= payoffs[i][1-j][1]-tolerance:
                equilibria.append((i, j))
    return equilibria

def mixed_nash(payoffs, tolerance=1e-12):
    """Return strictly interior mixed equilibrium, if uniquely identified.

    p = probability row player selects action 0;
    q = probability column player selects action 0.
    """
    _validate(payoffs)
    a00,a01,a10,a11 = (payoffs[i][j][0] for i,j in ((0,0),(0,1),(1,0),(1,1)))
    b00,b01,b10,b11 = (payoffs[i][j][1] for i,j in ((0,0),(0,1),(1,0),(1,1)))
    denom_q = a00-a01-a10+a11
    denom_p = b00-b01-b10+b11
    if abs(denom_q) <= tolerance or abs(denom_p) <= tolerance:
        return None
    q = (a11-a01)/denom_q
    p = (b11-b10)/denom_p
    if tolerance < p < 1-tolerance and tolerance < q < 1-tolerance:
        return {"row_action_0_probability": p, "column_action_0_probability": q}
    return None

def dominance(payoffs):
    _validate(payoffs)
    result = {"row": None, "column": None}
    for i in range(2):
        if all(payoffs[i][j][0] > payoffs[1-i][j][0] for j in range(2)):
            result["row"] = i
        if all(payoffs[j][i][1] > payoffs[j][1-i][1] for j in range(2)):
            result["column"] = i
    return result
