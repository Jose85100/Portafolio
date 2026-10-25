# 35. Distribuciones conjuntas y transformaciones

**Pregunta:** ¿cómo pasar de dos variables a sus márgenes, condicionales y funciones?  
**Objetivo:** integrar una densidad conjunta y justificar cambios de variable. **Antes:** integración, momentos y probabilidad condicional.

## 1. Una densidad vive sobre un soporte

Considera:
$$f_{X,Y}(x,y)=2,\quad0<x<y<1,$$
y cero fuera. El soporte es un triángulo, no todo el cuadrado unitario. Normalizamos:
$$\int_0^1\int_0^y2\,dx\,dy=\int_0^12y\,dy=1.$$
Si ignoramos los límites geométricos, obtendríamos una distribución distinta.

## 2. Obtener marginales

Para x fijo con 0<x<1, y puede ir de x a 1:
$$f_X(x)=\int_x^12\,dy=2(1-x).$$
Para y fijo:
$$f_Y(y)=\int_0^y2\,dx=2y.$$
Las dos densidades son cero fuera de (0,1), salvo convenciones irrelevantes en puntos de borde. Integrarlas individualmente da uno.

No hay independencia: f_X(x)f_Y(y)=4y(1−x), que no coincide con la conjunta. Además el soporte triangular excluye combinaciones que los márgenes permitirían por separado.

## 3. Condicionales para variables continuas

Donde f_Y(y)>0:
$$f_{X\mid Y}(x\mid y)=\frac{f_{X,Y}(x,y)}{f_Y(y)}
=\frac1y,\quad0<x<y.$$
Así X|Y=y es uniforme en (0,y), y:
$$E[X\mid Y=y]=y/2.$$
No hemos dividido entre P(Y=y), que es cero; la condicional continua se define mediante densidades.

La esperanza total da:
$$E[X]=E[Y/2]=\frac12\int_0^1y(2y)dy=\frac13.$$
Verificación por el margen:
$$\int_0^1x\,2(1-x)dx=1-\frac23=\frac13.$$

## 4. Transformación de una variable

Si Y=g(X) y g es estrictamente monótona y derivable con inversa adecuada:
$$f_Y(y)=f_X(g^{-1}(y))\left|\frac{d}{dy}g^{-1}(y)\right|.$$
Para una transformación creciente, la fórmula sale de F_Y(y)=F_X(g⁻¹(y)) y la regla de la cadena. En una decreciente cambia la orientación; el valor absoluto conserva positividad.

Si U es uniforme en (0,1) y Z=−ln U/λ:
$$U=e^{-\lambda Z},\quad\left|\frac{dU}{dZ}\right|=\lambda e^{-\lambda Z}.$$
Luego f_Z(z)=λe^(−λz), z>0: obtenemos una exponencial.

Si g no es uno a uno, hay que sumar contribuciones de cada rama. Para X uniforme en (−1,1), Z=X²:
$$F_Z(z)=P(-\sqrt z\le X\le\sqrt z)=\sqrt z,\quad0<z<1,$$
y f_Z(z)=1/(2√z). Ignorar una de las dos ramas daría la mitad de la masa.

## 5. Transformación conjunta y jacobiano

Para una transformación invertible de dos variables:
$$f_{U,V}(u,v)=f_{X,Y}(x(u,v),y(u,v))
\left|\det\frac{\partial(x,y)}{\partial(u,v)}\right|.$$
La matriz jacobiana corrige el cambio de áreas. Por ejemplo, con U=X,V=2Y, la inversa es X=U,Y=V/2 y el determinante es 1/2. También debemos transformar el soporte; el factor no basta por sí solo.

## Ejercicios y soluciones

1. En el triángulo, P(X<1/2)=∫₀^½2(1−x)dx=3/4.
2. E[X|Y=0.6]=0.3.
3. Si W=3X+2 con X uniforme en (0,1), W es uniforme en (2,5), con densidad 1/3.
4. ¿Una densidad que crece sin límite cerca de cero es inválida? No: 1/(2√z) integra uno en (0,1).

**Límite:** fórmulas de densidad no cubren sin adaptación variables con átomos o mezclas discretas–continuas.
