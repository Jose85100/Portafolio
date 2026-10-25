# 15. Trigonometría: ángulos, derivadas y ciclos

**Objetivo:** construir una oscilación y entender por qué las funciones trigonométricas aparecen en ciclos y aproximaciones.  
**Prerrequisitos:** funciones y derivadas. **Pregunta guía:** ¿cómo describir matemáticamente un movimiento que se repite?

## 1. Por qué usar radianes

Un ángulo en radianes se define como longitud de arco dividida por radio:
$$\theta=s/r.$$
Una vuelta completa recorre 2πr y por ello mide 2π radianes. Así:
$$180^\circ=\pi,\qquad 90^\circ=\pi/2.$$
Las fórmulas de derivación usuales suponen radianes. Si introduces grados sin convertirlos, aparece un factor de escala.

## 2. Seno y coseno desde el círculo

En el círculo unitario, el punto asociado al ángulo θ tiene coordenadas (cos θ, sin θ). Por Pitágoras:
$$\cos^2\theta+\sin^2\theta=1.$$
En un triángulo rectángulo, el seno es cateto opuesto sobre hipotenusa y el coseno cateto adyacente sobre hipotenusa. La definición circular permite extenderlos a todos los ángulos.

Rotar un punto un ángulo α y después β equivale a una rotación α+β. La multiplicación de las matrices de rotación produce:
$$
\cos(\alpha+\beta)=\cos\alpha\cos\beta-\sin\alpha\sin\beta,
$$
$$
\sin(\alpha+\beta)=\sin\alpha\cos\beta+\cos\alpha\sin\beta.
$$
Estas identidades no son reglas arbitrarias: codifican composición de rotaciones.

## 3. Derivar el seno

Por la definición de derivada y la identidad anterior:
$$
\frac{\sin(x+h)-\sin x}{h}
=\sin x\frac{\cos h-1}{h}+\cos x\frac{\sin h}{h}.
$$
En radianes, los límites fundamentales son sin(h)/h→1 y (cos h−1)/h→0. El primero puede justificarse geométricamente mediante comparación de áreas para 0<h<π/2 y el teorema del encaje; la simetría cubre h<0. El segundo se deduce de cos h−1=−2sin²(h/2).

Por tanto:
$$\frac{d}{dx}\sin x=\cos x.$$
Análogamente, (cos x)'=−sin x. La condición de radianes explica que no aparezcan constantes adicionales.

## 4. Construir un ciclo interpretable

Sea:
$$y(t)=m+A\sin(\omega t+\phi),\quad A>0,\ \omega>0.$$
m es nivel central, A amplitud, ω frecuencia angular y φ fase. Como el seno repite su valor al añadir 2π:
$$T=\frac{2\pi}{\omega}.$$
El máximo es m+A y el mínimo m−A. No confundas amplitud con distancia entre máximo y mínimo: esa distancia es 2A.

**Ejemplo mensual.**
$$y(t)=100+20\sin(2\pi t/12).$$
El periodo es 12 meses; máximo 120 en t=3+12k y mínimo 80 en t=9+12k. La derivada:
$$y'(t)=\frac{10\pi}{3}\cos(\pi t/6)$$
mide cambio en unidades de y por mes. En el máximo la derivada es cero, aunque el nivel sea alto.

## 5. Muestrear puede ocultar la oscilación

Si observas sin(2πt) solo en t=0,1,2,…, obtienes siempre cero. La función oscila, pero los puntos elegidos no lo muestran. Esta ambigüedad de muestreo advierte contra interpretar series observadas sin revisar su frecuencia.

## Ejercicios y soluciones

1. Convierte 60° a radianes: π/3.
2. En y=5+2cos(πt), el periodo es 2, máximo 7 y mínimo 3.
3. Deriva sin(3t): 3cos(3t), por la cadena.
4. ¿Dos años de ventas bastan para establecer un ciclo estable anual? No necesariamente: tendencias, calendario, ruido y cambios de régimen pueden confundirse con estacionalidad.

**Aplicación y límite:** las ondas son componentes descriptivos útiles; una periodicidad ajustada no demuestra una causa económica ni garantiza repetición futura.
