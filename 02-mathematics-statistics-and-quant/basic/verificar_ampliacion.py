"""Referencias numéricas de las lecciones 25–40; no sustituyen demostraciones."""
from fractions import Fraction as F
from itertools import product
from math import sqrt, exp, log, pi, comb, erf, isclose
import cmath

def cerca(a,b,tol=1e-10):
    assert isclose(a,b,rel_tol=tol,abs_tol=tol),(a,b)

# 25–26: cotas e identidades de los argumentos.
assert all(1-1/(n+1)>1-1/n for n in range(1,100))
assert 1/100==.01 and 1/101<.01
assert all(2**n>=n+1 for n in range(101))
assert all(sum(2*k-1 for k in range(1,n+1))==n*n for n in range(1,101))
# 27: factorización, discriminante y raíces extrañas.
for x in [-3,0,1,2,3,5,F(1,2)]:
    assert x**3-6*x*x+11*x-6==(x-1)*(x-2)*(x-3)
assert sqrt(2+2)==2 and sqrt(-1+2)!=-1
assert sqrt(2*3+3)==3 and sqrt(2*(-1)+3)!=-1
# 28: operaciones complejas y raíces.
assert (1+2j)*(3-1j)==5+5j
assert abs((1+2j)/(3-1j)-(.1+.7j))<1e-12
assert (1+1j)**4==-4
for k in range(3):
    assert abs(cmath.exp(2j*pi*k/3)**3-1)<1e-12
# 29: logit, duplicación y odds.
logistica=lambda z: 1/(1+exp(-z)) if z>=0 else exp(z)/(1+exp(z))
cerca(logistica(log(3)),.75)
cerca(logistica(log(2)),F(2,3))
cerca(log(2)/.05,13.862943611198906)
cerca(log(2)/log(1.05),14.206699082890461)
cerca(2*.1*.9,.18)
# 30: solución general y núcleo.
for t in [F(-2),F(0),F(3,2)]:
    x=[2-t,1-t,t]
    assert x[0]+2*x[1]+3*x[2]==4 and x[1]+x[2]==1
assert -1-2+3==0 and -1+1==0
# 31: autovectores y positividad.
def matvec(A,x): return [sum(a*b for a,b in zip(row,x)) for row in A]
A=[[2,1],[1,2]]
assert matvec(A,[1,1])==[3,3]
assert matvec(A,[1,-1])==[1,-1]
cerca(sqrt(.04*.09),.06)
# 32: epsilon-delta y pendientes.
for eps in [.001,.1,1,10]:
    delta=min(1,eps/5)
    for signo in [-1,1]:
        x=2+signo*delta*.99
        assert abs(x*x-4)<eps
assert (3**2-1**2)/(3-1)==4
# 33: garantías de bisección, Newton, descenso y ciclo.
a,b=1.,2.
for _ in range(10):
    m=(a+b)/2
    if (a*a-2)*(m*m-2)<0:b=m
    else:a=m
assert abs((a+b)/2-sqrt(2))<=1/2048
x=1.
for _ in range(5):x=(x+2/x)/2
cerca(x,sqrt(2))
x=7.
x=x-.25*2*(x-3);cerca(x,5)
x=x-.25*2*(x-3);cerca(x,4)
f=lambda x:x**3-2*x+2
df=lambda x:3*x*x-2
assert 0-f(0)/df(0)==1 and 1-f(1)/df(1)==0
# 34: distribuciones y momentos.
cerca(comb(10,2)*.2**2*.8**8,.301989888)
cerca(.9**5,.59049)
cerca(3*exp(-3),.14936120510359183)
assert F(1,1)/F(1,5)==5
# 35: integrales de polinomios y condicionamiento.
# f_X=2(1-x); primitiva 2x-x².
cerca(2*.5-.5**2,.75)
assert F(1)-F(2,3)==F(1,3)
cerca(.6/2,.3)
# Integración exacta de monomios: densidad conjunta, marginales y media.
assert F(2,2)==1
assert F(2,2)-F(2,3)==F(1,3)
# 36: potencia y multiplicidad; Φ mediante erf.
Phi=lambda z:(1+erf(z/sqrt(2)))/2
potencia=1-Phi(1.96-2)+Phi(-1.96-2)
cerca(potencia,.5159909117345218)
cerca(2*(1-Phi(2)),.04550026389635842)
cerca(2*(1-Phi(1)),.31731050786291415)
cerca(1-.95**20,.6415140775914581)
# 37: enumeración exacta de bootstrap, sin ruido Monte Carlo.
medias=[sum(map(F,m))/3 for m in product([1,2,3],repeat=3)]
centro=sum(medias)/len(medias)
varianza=sum((m-centro)**2 for m in medias)/len(medias)
assert centro==2 and varianza==F(2,9)
cerca(20/(sqrt(100)*100),.02)
assert 96.15<100*exp(-1.96*.02)<96.16
assert 103.99<100*exp(1.96*.02)<104.01
# 38: condiciones iniciales, derivadas y estabilidad de Euler.
cerca(5*(1-exp(-2*0)),0)
for t in [0,.1,1,3]:
    y=5*(1-exp(-2*t))
    cerca(10*exp(-2*t),10-2*y)
    y=100/(1+9*exp(-t))
    cerca(900*exp(-t)/(1+9*exp(-t))**2,y*(1-y/100))
assert (100-10)/10==9
assert 1-2*1==-1
# 39: transición y equilibrio Markov con fracciones.
P=[[F(9,10),F(1,10)],[F(1,5),F(4,5)]]
def trans(p,P):return [sum(p[i]*P[i][j] for i in range(len(p))) for j in range(len(p))]
assert trans(trans([F(1),F(0)],P),P)==[F(83,100),F(17,100)]
assert trans([F(2,3),F(1,3)],P)==[F(2,3),F(1,3)]
cerca(1-.8**3,.488)
# 40: QR y ortogonalidad de residuos.
dot=lambda x,y:sum(a*b for a,b in zip(x,y))
q1=[1/sqrt(2),1/sqrt(2),0]
q2=[1/sqrt(6),-1/sqrt(6),2/sqrt(6)]
cerca(dot(q1,q2),0);cerca(dot(q1,q1),1);cerca(dot(q2,q2),1)
cerca(dot(q1,[1,2,3]),3/sqrt(2))
cerca(dot(q2,[1,2,3]),5/sqrt(6))
beta=[F(2,3),F(5,3)]
prediction=[sum(beta),beta[0],beta[1]]
res=[F(y)-yh for y,yh in zip([1,2,3],prediction)]
assert res==[F(-4,3),F(4,3),F(4,3)]
assert dot(res,[1,1,0])==0 and dot(res,[1,0,1])==0
assert dot(res,res)==F(16,3)
print("OK: referencias numéricas de las 16 lecciones 25–40.")

