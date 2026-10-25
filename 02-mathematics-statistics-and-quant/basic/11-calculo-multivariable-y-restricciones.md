# 11. Cálculo multivariable y restricciones

**Objetivo:** pasar de una pendiente a varias direcciones de cambio. Prerrequisitos: álgebra lineal y cálculo diferencial.

## Parciales y gradiente

Para $f(x,y)=x^2+3y^2$, derivar respecto de x manteniendo y fija da $f_x=2x$; análogamente $f_y=6y$. El gradiente es $(2x,6y)$. Cerca de (1,1), un cambio pequeño (dx,dy) produce aproximadamente $df=2dx+6dy$. La aproximación pierde exactitud para desplazamientos grandes.

La matriz Hessiana contiene segundas derivadas. Aquí es diagonal con entradas 2 y 6. Para todo vector no nulo v, $v^THv>0$; la función es estrictamente convexa y su punto estacionario (0,0) es mínimo global. Una Hessiana indefinida puede producir un punto silla, como en $x^2-y^2$.

## Una restricción cambia el óptimo

Minimiza $x^2+y^2$ sujeto a $x+y=1$. Sustituir y=1-x produce $2x^2-2x+1$, cuya derivada se anula en x=1/2. Entonces y=1/2 y el valor mínimo es 1/2.

Con Lagrange:
$$L=x^2+y^2-\lambda(x+y-1).$$
Las condiciones $2x=\lambda$, $2y=\lambda$ y x+y=1 dan la misma solución. La convexidad y la restricción afín justifican globalidad. Las condiciones de primer orden por sí solas no siempre bastan, y requieren condiciones de regularidad.

## Interpretar el multiplicador

Con restricción x+y=c, la solución es x=y=c/2 y el valor óptimo V(c)=c²/2. Por tanto V'(c)=c. El multiplicador también vale c: mide cómo cambia localmente el valor óptimo al modificar el lado derecho, con la convención de signo de L elegida.

## Ejercicios con solución

1. Gradiente de xy+x²: (y+2x,x).
2. ¿Es (0,0) mínimo de xy? No: sobre y=x la función es positiva y sobre y=-x negativa.
3. Minimiza x²+3y² con x+y=1. De 2x=λ y 6y=λ sale x=3y; solución (3/4,1/4), valor 3/4.

**Aplicación:** en portafolios, los pesos suelen sumar uno; optimizar ignorando esa restricción resuelve otro problema.

