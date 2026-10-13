"""Minimal reproducible economic research kernels (standard library only)."""
import math
import random

def ols(x, y):
    """OLS with intercept; requires nonzero regressor variance."""
    if len(x)!=len(y) or len(x)<3: raise ValueError("Need >=3 paired observations")
    mx=sum(x)/len(x); my=sum(y)/len(y)
    ss=sum((v-mx)**2 for v in x)
    if ss<=1e-12: raise ValueError("Regressor has no variation")
    b=sum((a-mx)*(c-my) for a,c in zip(x,y))/ss
    return my-b*mx,b

def predict(coef,x):
    return [coef[0]+coef[1]*v for v in x]

def rmse(y, yhat):
    if not y or len(y)!=len(yhat): raise ValueError("Invalid predictions")
    return math.sqrt(sum((a-b)**2 for a,b in zip(y,yhat))/len(y))

def bootstrap_slope(x,y,replications=200,seed=42):
    if replications<1: raise ValueError("replications must be positive")
    rng=random.Random(seed); n=len(x); values=[]
    for _ in range(replications):
        ix=[rng.randrange(n) for _ in range(n)]
        try: values.append(ols([x[i] for i in ix],[y[i] for i in ix])[1])
        except ValueError: pass
    if not values: raise ValueError("No valid bootstrap draws")
    values.sort()
    return values[int(.025*(len(values)-1))],values[int(.975*(len(values)-1))]

def generate_panel(n=180,seed=42,intercept=1.5,slope=0.8,noise=0.25):
    if n<3 or noise<0: raise ValueError("Invalid simulation parameters")
    rng=random.Random(seed)
    x=[rng.gauss(0,1) for _ in range(n)]
    y=[intercept+slope*v+rng.gauss(0,noise) for v in x]
    return x,y

def expected_credit_loss(pd,lgd,ead):
    if not(len(pd)==len(lgd)==len(ead)): raise ValueError("Length mismatch")
    if any(not(0<=p<=1 and 0<=l<=1 and e>=0) for p,l,e in zip(pd,lgd,ead)):
        raise ValueError("Invalid PD/LGD/EAD")
    return sum(p*l*e for p,l,e in zip(pd,lgd,ead))

def markov_step(probabilities,transition):
    n=len(probabilities)
    if not n or len(transition)!=n or any(len(row)!=n for row in transition): raise ValueError("Invalid dimensions")
    if any(p<0 for p in probabilities) or abs(sum(probabilities)-1)>1e-8: raise ValueError("Invalid state distribution")
    if any(any(v<0 for v in row) or abs(sum(row)-1)>1e-8 for row in transition): raise ValueError("Transition rows must sum to 1")
    return [sum(probabilities[i]*transition[i][j] for i in range(n)) for j in range(n)]

def best_response_grid(payoff,actions):
    if not actions: raise ValueError("Empty action set")
    return max(actions,key=payoff)
