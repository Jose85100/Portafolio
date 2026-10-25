"""Comprueba ejemplos de las lecciones 14–24. No sustituye demostraciones."""
from math import exp, log, pi, sin, cos, sqrt, isclose, comb
from fractions import Fraction as F

def cerca(a, b):
    assert isclose(a, b, rel_tol=1e-9, abs_tol=1e-9), (a, b)

# 14: extremos de intervalos y cota del producto.
assert abs(2*(-1)-3)==5 and abs(2*4-3)==5
assert all((x-1)/(x+2)>=0 for x in [-10,-3,1,2,10])
assert (0-1)/(0+2)<0
assert 5*5==10**2/4
# 15: periodo y derivada analítica.
periodo=2*pi/(2*pi/12)
cerca(periodo,12)
cerca(100+20*sin(2*pi*3/12),120)
cerca(100+20*sin(2*pi*9/12),80)
cerca((10*pi/3)*cos(pi*3/6),0)
# 16: elasticidad local frente a variación finita.
cerca(1/1.1**2,0.8264462809917354)
assert abs((1/1.1**2-1)-(-.2))>.02
# 17: evaluar antiderivadas e integrales impropias.
cerca((1-1)*exp(1)-(0-1)*exp(0),1)
cerca(log(5)/2,0.8047189562170501)
cerca(1/2,(-1/1e12)-(-1/2))
# 18: densidad triangular, momentos, cuantiles.
media=F(4,3)
segundo=F(2)
assert segundo-media**2==F(2,9)
cerca((2*sqrt(.9))**2/4,.9)
cerca(exp(-.5*2),exp(-1))
# 19: varianza de combinación y ley de varianza total.
cerca(.5**2*.04+.5**2*.09+2*.5*.5*.01,.0375)
mu=.8*10+.2*20
cerca(mu,12)
cerca(.8*4+.2*9,5)
cerca(.8*(10-mu)**2+.2*(20-mu)**2,16)
# 20: score Bernoulli y varianza normal ML.
p=7/100
cerca(7/p-93/(1-p),0)
cerca(sqrt(p*(1-p)/100),.02551470164434615)
assert sum((x-2)**2 for x in [1,2,3])/3==2/3
# 21: ecuaciones normales, residuos y error exacto.
a,b=F(1,3),F(3,2)
xs,ys=[1,2,3],[2,3,5]
res=[y-a-b*x for x,y in zip(xs,ys)]
assert res==[F(1,6),F(-1,3),F(1,6)]
assert sum(res)==0 and sum(x*e for x,e in zip(xs,res))==0
assert sum(e*e for e in res)==F(1,6)
# 22: Chebyshev y tamaño de muestra.
cerca(.16/(1280*.05**2),.05)
assert 12/sqrt(36)==2 and 12/sqrt(144)==1
# 23: Jensen en distribución de dos puntos.
cerca((log(50)+log(150))/2,log(sqrt(50*150)))
assert (log(50)+log(150))/2<log(100)
# 24: actualización Beta, varianza y combinación ponderada.
alpha,beta,n,k=2,8,20,4
aa,bb=alpha+k,beta+n-k
cerca(aa/(aa+bb),.2)
assert F(aa*bb,(aa+bb)**2*(aa+bb+1))==F(4,775)
cerca((alpha+beta)/(alpha+beta+n)*alpha/(alpha+beta)+n/(alpha+beta+n)*k/n,aa/(aa+bb))
cerca((2+0)/(2+8+20),1/15)
print("OK: ejemplos y relaciones numéricas de las once lecciones.")
