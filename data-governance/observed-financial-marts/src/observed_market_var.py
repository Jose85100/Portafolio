"""Rolling historical VaR and ES using observed adjusted prices from read-only SQLite."""
import argparse, json, math, sqlite3
from pathlib import Path

def tail(values, alpha):
    v=sorted(values)
    k=max(1, math.ceil(alpha*len(v)))
    return -v[k-1], -sum(v[:k])/k

def backtest(prices, window=250, alpha=.01):
    if len(prices) <= window+1 or window < 100 or not 0<alpha<1:
        raise ValueError("Insufficient data")
    r=[math.log(prices[i]/prices[i-1]) for i in range(1,len(prices))]
    if any(not math.isfinite(x) for x in r):
        raise ValueError("Nonfinite returns")
    exceptions=0
    last=None
    for i in range(window,len(r)):
        var,es=tail(r[i-window:i],alpha)
        exceptions+=int(r[i] < -var)
        last=(var,es)
    n=len(r)-window
    p=exceptions/n
    def term(k,prob):
        return 0 if k==0 else k*math.log(prob)
    lr=2*(term(exceptions,p)+term(n-exceptions,1-p)-
          term(exceptions,alpha)-term(n-exceptions,1-alpha))
    return dict(coverage=n,exceptions=exceptions,exception_rate=p,
                expected_exception_rate=alpha,kupiec_p=math.erfc(math.sqrt(max(0,lr)/2)),
                last_var=last[0],last_es=last[1],production_approved=False)

def run(path,symbol):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True)
    try:
        data=db.execute("SELECT date,adjusted_close FROM prices WHERE symbol=? ORDER BY date",(symbol,)).fetchall()
    finally:
        db.close()
    if any(v is None or v<=0 for _,v in data):
        raise ValueError("Invalid adjusted price")
    result=backtest([v for _,v in data])
    result.update(symbol=symbol,observations=len(data),latest_date=data[-1][0],
                  source="InvestmentOS canonical Google Drive",vintage_verified=False)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--db",required=True)
    p.add_argument("--symbol",default="SPY")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=run(a.db,a.symbol)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
