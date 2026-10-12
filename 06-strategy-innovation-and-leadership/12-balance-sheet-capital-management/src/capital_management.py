"""Capital-constrained business growth; stylized risk-weighted assets."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class BusinessLine:
    name: str
    rwa_per_unit: float
    expected_profit_per_unit: float
    maximum_units: int

def optimize(capital, minimum_capital_ratio, lines, step=1):
    if not all(isfinite(v) for v in (capital,minimum_capital_ratio)):
        raise ValueError("nonfinite parameters")
    if capital<0 or not 0<minimum_capital_ratio<=1 or not isinstance(step,int) or step<=0:
        raise ValueError("invalid capital parameters")
    if not lines or len(lines)>10 or len({x.name for x in lines})!=len(lines):
        raise ValueError("invalid business lines")
    for line in lines:
        if not line.name or not isfinite(line.rwa_per_unit) or not isfinite(line.expected_profit_per_unit):
            raise ValueError("invalid business line")
        if line.rwa_per_unit<=0 or not isinstance(line.maximum_units,int) or not 0<=line.maximum_units<=100:
            raise ValueError("invalid RWA or volume")
    capacity=capital/minimum_capital_ratio
    best={"expected_profit":0.0,"rwa":0.0,"allocation":{}}
    def visit(i,rwa,profit,allocation):
        nonlocal best
        if i==len(lines):
            if profit>best["expected_profit"]+1e-10:
                best={"expected_profit":profit,"rwa":rwa,"allocation":allocation.copy()}
            return
        line=lines[i]
        values=list(range(0,line.maximum_units+1,step))
        if values[-1]!=line.maximum_units:
            values.append(line.maximum_units)
        for units in values:
            next_rwa=rwa+units*line.rwa_per_unit
            if next_rwa<=capacity+1e-10:
                allocation[line.name]=units
                visit(i+1,next_rwa,profit+units*line.expected_profit_per_unit,allocation)
        allocation.pop(line.name,None)
    visit(0,0,0,{})
    best["capital_ratio"]=capital/best["rwa"] if best["rwa"] else None
    best["rwa_capacity"]=capacity
    return best
