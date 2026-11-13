# 38. Ecuaciones diferenciales: evolución, equilibrio y discretización

**Pregunta:** ¿cómo describir cambios continuos y qué sucede al aproximarlos por pasos?  
**Objetivo:** resolver modelos lineales y logísticos e interpretar Euler. **Antes:** derivadas, integración y recurrencias.

## 1. Crecimiento proporcional

En y'=ry con y(0)=y₀>0, separar variables da:
$$\frac{dy}{y}=r\,dt\Rightarrow y(t)=y_0e^{rt}.$$
La solución cero también existe, aunque dividir por y la excluye durante la derivación. Las soluciones con y₀ negativo se verifican mediante la misma fórmula usando ln|y| en la separación.

Si r<0, las trayectorias se acercan a cero; si r>0, se alejan salvo que inicien exactamente en cero.

## 2. Modelo lineal con entrada constante

Resuelve y'=a−by, b>0. El equilibrio es y*=a/b. Define z=y−y*. Entonces:
$$z'=a-b(z+a/b)=-bz.$$
Por el caso anterior:
$$y(t)=\frac ab+\left(y_0-\frac ab\right)e^{-bt}.$$
La distancia al equilibrio decrece exponencialmente. La escala 1/b es el tiempo en que esa distancia se multiplica por e⁻¹.

Con a=10,b=2,y₀=0:
$$y(t)=5(1-e^{-2t}).$$
Su derivada inicial es 10 y el límite de largo plazo es 5. No confundas el flujo inicial con el nivel de equilibrio.

## 3. Crecimiento logístico

Para r,K>0:
$$y'=ry(1-y/K).$$
Los equilibrios son 0 y K. Para una solución con 0<y<K:
$$\frac{dy}{y(1-y/K)}=r\,dt.$$
La fracción se descompone:
$$\frac1{y(1-y/K)}=\frac1y+\frac1{K-y}.$$
Integrar produce ln y−ln(K−y)=rt+C. Despejando:
$$y(t)=\frac K{1+Ae^{-rt}},\quad A=\frac{K-y_0}{y_0}.$$
Para y₀>0, esta fórmula también se verifica directamente, incluyendo y₀>K; los equilibrios se estudian aparte.

El crecimiento absoluto es máximo en y=K/2 porque ry−ry²/K es una parábola cóncava. El crecimiento proporcional y'/y=r(1−y/K) disminuye al aumentar y.

## 4. Estabilidad local

Para y'=f(y), la linealización cerca de y* usa:
$$z'\approx f'(y^*)z.$$
Si f'(y*)<0, pequeñas desviaciones decaen localmente; si es >0, crecen. Si es cero, esta prueba no decide.

En la logística, f'(y)=r−2ry/K. En cero vale r>0: equilibrio inestable. En K vale −r<0: estable. Es una conclusión local; la fórmula explícita permite estudiar además las trayectorias positivas.

## 5. Euler puede cambiar la estabilidad

El método explícito:
$$y_{k+1}=y_k+h f(y_k)$$
aproxima la derivada por un cociente. Para z'=−bz:
$$z_{k+1}=(1-bh)z_k.$$
Aunque el sistema continuo sea estable para todo b>0, la aproximación converge solo si:
$$|1-bh|<1\iff0<h<2/b.$$
Un paso demasiado grande genera oscilación creciente artificial. Para 0<h<1/b, el factor es positivo y la aproximación decae sin alternar.

## Ejercicios y soluciones

1. En y'=6−3y, el equilibrio es 2 y y(t)=2+(y₀−2)e^(−3t).
2. Para logística con K=100,y₀=10, A=9.
3. Euler con b=2,h=1 da factor −1: no decae, aunque la solución exacta sí.
4. ¿Un paso menor elimina todo error? No: reduce discretización bajo condiciones adecuadas, pero hay redondeo y otros errores de modelación.

**Límite:** las soluciones requieren parámetros y condiciones iniciales coherentes; crecimiento económico real no queda validado por usar una ecuación conocida.
