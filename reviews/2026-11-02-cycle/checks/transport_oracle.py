"""Independent finite-sample Decimal100 check of the real C++ consumer.

Run from streaming-moments with its built executable; producer API is reused,
but numerical oracle is calculated independently from the received binary64s.
"""
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import random
import subprocess
import sys
sys.path.insert(0, str(Path.cwd()))
from src.dynamic import DynamicMoments
from src.transport import export_state
rng=random.Random(1102)
maximum_relative_normal=0.0
maximum_ulp=0.0
for case in range(1000):
    n=rng.randint(4,50)
    exponent=rng.randint(-1070,1020)
    xs=[math.ldexp(rng.uniform(-1,1),exponent-rng.randint(0,20)) for _ in range(n)]
    split=rng.randint(1,n-1)
    left,right=DynamicMoments(),DynamicMoments()
    for x in xs[:split]:left=left.push(x)
    for x in xs[split:]:right=right.push(x)
    ddof=case%2
    with localcontext() as context:
        context.prec=100
        values=[Decimal.from_float(x) for x in xs]
        mean=sum(values)/n
        expected=float((sum((x-mean)**2 for x in values)/(n-ddof)).sqrt())
    output=subprocess.check_output(['.build/moments_consumer',str(ddof)],input=export_state(left)+'\n'+export_state(right)+'\n',text=True).splitlines()
    answer=json.loads(output[1]);sd=answer['std']
    if sd is None:
        assert expected==0.0 and answer['status']=='std_underflow'
        continue
    error=abs(sd-expected)
    assert error<=max(4*math.ulp(expected),1e-12*abs(expected)),(case,answer,expected)
    maximum_ulp=max(maximum_ulp,error/math.ulp(expected))
    if expected>=sys.float_info.min:
        maximum_relative_normal=max(maximum_relative_normal,error/expected)
print(json.dumps(dict(seed=1102,cases=1000,max_relative_sd_normal=maximum_relative_normal,max_ulp_sd=maximum_ulp,scope='finite synthetic inputs; not a universal floating-point guarantee')))
