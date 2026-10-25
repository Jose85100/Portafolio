"""Verificaciones didácticas. Ejecutar con Python 3, sin dependencias."""
from math import isclose, log, sqrt
from statistics import mean, median, variance, pvariance

def cerca(actual, esperado, tolerancia=1e-10):
    assert isclose(actual, esperado, rel_tol=tolerancia, abs_tol=tolerancia), (actual, esperado)

def trapecios(f, a, b, n):
    h = (b-a)/n
    return h*(0.5*f(a) + sum(f(a+i*h) for i in range(1,n)) + 0.5*f(b))

# Álgebra: sustituir y conservar dominio.
assert 4*(5-2) == 12
cerca(1.2*0.8, 0.96)
cerca(100*1.1**2, 121)
cerca(log(2*3), log(2)+log(3))
# Funciones: composición y equilibrio.
q = 100/3
cerca(5*q, 100+2*q)
assert (2+1)**2 != 2**2+1
# Álgebra lineal: residuo del sistema y forma cuadrática.
x, y = 1, 2
assert x+y == 3 and 2*x-y == 0
cerca(0.6*0.05+0.4*(-0.02), 0.022)
v = 0.6**2*0.04+2*0.6*0.4*0.01+0.4**2*0.09
cerca(v, 0.0336)
assert sqrt(v) > 0
# Derivada: diferencia central frente al resultado analítico.
h = 1e-4
cerca(((3+h)**2-(3-h)**2)/(2*h), 6, 1e-8)
beneficio = lambda q: 10*q-q*q-9
assert beneficio(5) == 16
assert all(beneficio(q) <= 16 for q in range(21))
# Integración: solución exacta y mejora al refinar malla.
cerca(trapecios(lambda x: 2*x, 0, 3, 8), 9)
errores = [abs(trapecios(lambda x: x*x, 0, 1, n)-1/3) for n in (1,2,4)]
cerca(errores[0]/errores[1], 4)
cerca(errores[1]/errores[2], 4)
cerca(100+2*10+0.05*10**2, 125)
# Probabilidad: Bayes frente a tabla de conteos.
posterior = 0.9*0.01/(0.9*0.01+0.05*0.99)
cerca(posterior, 90/(90+495))
cerca(posterior, 2/13)
cerca(1000*0.4*0.05, 20)
# Estadística: población, muestra e intervalo t (cuantil tabulado).
datos = [1,2,3,4,10]
assert mean(datos) == 4 and median(datos) == 3
cerca(pvariance(datos), 10)
cerca(variance(datos), 12.5)
cerca(10-2.064*2/sqrt(25), 9.1744)
cerca(variance([2*x for x in datos]), 4*variance(datos))
xs, ys = [1,2,3], [2,3,5]
mx, my = mean(xs), mean(ys)
b = sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
a = my-b*mx
cerca(b, 1.5)
cerca(a, 1/3)
print("OK: ejemplos de los siete módulos verificados.")
