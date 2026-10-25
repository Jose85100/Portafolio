# 33. Buscar raíces y minimizar: tres algoritmos distintos

**Pregunta:** ¿cómo pasar de una ecuación a un procedimiento verificable?  
**Objetivo:** derivar bisección, Newton y descenso de gradiente, con criterios de parada. **Antes:** límites, derivadas y convexidad.

## 1. Bisección: conservar una raíz encerrada

Si f es continua en [a,b] y f(a)f(b)<0, existe una raíz interior. Calcula m=(a+b)/2. Si f(m)=0, terminamos. Si no, conserva la mitad cuyos extremos tienen signos opuestos.

Después de n reducciones, el intervalo mide (b₀−a₀)/2ⁿ. Su punto medio aproxima alguna raíz encerrada con error como máximo:
$$\frac{b_0-a_0}{2^{n+1}}.$$
Esta es una garantía sobre ubicación, no solo sobre el valor de f.

Para x²−2 en [1,2], las primeras mitades conservadas son [1,1.5], [1.25,1.5] y [1.375,1.5]. Se mantienen continuidad y cambio de signo en cada paso. La convergencia es robusta, aunque no especialmente rápida.

## 2. Newton: resolver una tangente

Aproximamos f cerca de xₖ:
$$f(x)\approx f(x_k)+f'(x_k)(x-x_k).$$
La raíz de esa recta produce:
$$x_{k+1}=x_k-\frac{f(x_k)}{f'(x_k)},$$
si f'(xₖ)≠0. Para f=x²−2:
$$x_{k+1}=\frac12\left(x_k+\frac2{x_k}\right).$$
Desde x₀=1, obtenemos 1.5, 1.416666…, 1.414215….

Cuando f tiene segunda derivada suficientemente regular y la raíz es simple, Newton tiene convergencia local cuadrática: cerca de la raíz, el error siguiente es de orden del cuadrado del actual. «Local» importa: un punto inicial distante puede divergir o caer en un ciclo.

Para f=x³−2x+2, Newton desde 0 pasa a 1 y desde 1 vuelve a 0. Tener una función suave no garantiza convergencia desde cualquier inicio.

## 3. Minimizar no es buscar una raíz de la función

Para minimizar g, el descenso de gradiente usa:
$$x_{k+1}=x_k-\eta g'(x_k),\quad\eta>0.$$
Busca reducir el objetivo siguiendo la dirección opuesta a su pendiente. No intenta imponer g(x)=0.

Para g(x)=(x−3)²:
$$x_{k+1}-3=(1-2\eta)(x_k-3).$$
De aquí obtenemos una condición exacta de convergencia:
$$|1-2\eta|<1\iff0<\eta<1.$$
Si η=0.25, el error se divide por dos por iteración. Si η=1, oscila con amplitud constante; si η>1, crece. Un paso grande puede empeorar la solución.

## 4. Extensión cuadrática

Si g(x)=xᵀHx/2−bᵀx con H simétrica definida positiva:
$$x_{k+1}=x_k-\eta(Hx_k-b).$$
En las direcciones de autovectores de H, cada error se multiplica por 1−ηλᵢ. Por eso:
$$0<\eta<2/\lambda_{\max}$$
garantiza convergencia. Las direcciones con autovalores pequeños pueden converger lentamente, vinculando optimización y condición numérica.

## 5. Parar con una razón

Un residual |f(x)| pequeño no siempre implica un error |x−r| pequeño: si la función es casi plana, pueden ser muy distintos. Combina límite de iteraciones, criterio de paso y residual; cuando hay intervalo de bisección, informa también su ancho. No ocultes una terminación por agotamiento como convergencia.

## Ejercicios y soluciones

1. Tras 10 reducciones de un intervalo inicial de ancho 1, el error del punto medio no supera 1/2048.
2. Newton para x²−2 desde 2 da x₁=1.5.
3. Descenso para (x−3)², η=0.25, x₀=7: x₁=5, x₂=4.
4. ¿Gradiente cero implica mínimo? No: x³ en cero es estacionaria sin mínimo.

**Aplicación:** elegir un algoritmo exige saber qué se busca y qué garantías ofrecen sus supuestos.
