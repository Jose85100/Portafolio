# 29. Exponencial, logaritmo y función logística

**Pregunta:** ¿cómo representar crecimiento proporcional y probabilidades sin salir de (0,1)?  
**Objetivo:** derivar crecimiento continuo, duplicación y transformación logística. **Antes:** funciones, logaritmos y derivadas.

## 1. Del crecimiento discreto al continuo

Si V aumenta proporcionalmente a su nivel a tasa continua r:
$$V'(t)=rV(t),\quad V(0)=V_0>0.$$
Separando variables e integrando:
$$\int\frac{dV}{V}=\int r\,dt\Rightarrow\ln V=rt+C.$$
La condición inicial da C=ln V₀ y:
$$V(t)=V_0e^{rt}.$$
Derivar verifica el modelo y sustituir t=0 verifica la condición inicial.

r tiene unidades de tiempo inverso. No mezcles una tasa mensual con t en años sin convertirla. Una tasa efectiva anual j corresponde a r=ln(1+j) por año, no a r=j exactamente.

## 2. Tiempo de duplicación

Si r>0, resolver V(T)=2V₀:
$$e^{rT}=2\Rightarrow T=\frac{\ln2}{r}.$$
Para r=0.05 por año, T≈13.8629 años. Una tasa efectiva anual de 5% produce T=ln2/ln1.05≈14.2067 años; son convenciones diferentes de tasa.

Para r=0, el capital permanece constante y no existe tiempo finito de duplicación. Para r<0, decrece; en cambio, su vida media es ln2/|r|.

## 3. Derivar la función logística desde odds

Para una probabilidad p∈(0,1), sus odds son p/(1−p). No son lo mismo que p: con p=0.2, odds=0.25. Supongamos:
$$\ln\frac p{1-p}=z.$$
Exponenciar da p/(1−p)=eᶻ. Despejando:
$$p=e^z(1-p)\Rightarrow p(1+e^z)=e^z,$$
$$p=\frac{e^z}{1+e^z}=\frac1{1+e^{-z}}.$$
Esta transformación lleva todos los reales al intervalo abierto (0,1). Su inversa es el logit, definido solo en ese intervalo.

## 4. Pendiente e interpretación

Para p(z)=(1+e^(−z))⁻¹:
$$p'(z)=\frac{e^{-z}}{(1+e^{-z})^2}=p(z)(1-p(z)).$$
Siempre es positiva y alcanza su máximo 1/4 cuando p=1/2. La segunda derivada:
$$p''(z)=p(1-p)(1-2p)$$
cambia de signo en z=0: la curva no es globalmente convexa ni globalmente cóncava.

Si z=a+bx, por la cadena:
$$\frac{dp}{dx}=bp(1-p).$$
Un coeficiente b constante no implica un cambio constante de probabilidad. Sí implica que aumentar x en una unidad multiplica los odds por eᵇ, manteniendo los demás términos fijos.

**Ejemplo:** si a=0 y b=ln2, x=0 da p=1/2 y x=1 da odds=2, p=2/3. Duplicar odds no duplica la probabilidad.

## 5. Cuidado computacional

Para z muy negativo, calcular e^(−z) directamente puede desbordar. Una implementación estable usa 1/(1+e^(−z)) si z≥0 y eᶻ/(1+eᶻ) si z<0. En matemáticas el resultado está estrictamente entre cero y uno; el redondeo puede producir extremos exactos en una máquina.

## Ejercicios y soluciones

1. Logit de p=0.8: ln4.
2. Logística de ln3: 3/4.
3. Con b=2 y p=0.1, la pendiente local respecto a x es 2·0.1·0.9=0.18.
4. ¿Usar una logística garantiza calibración de un modelo de riesgo? No: garantiza rango matemático, pero calibración y capacidad predictiva requieren evaluación.

**Conexión:** las tasas continuas describen una ley de evolución; la logística parametriza probabilidades. Elegir una forma funcional no valida automáticamente el mecanismo económico.
