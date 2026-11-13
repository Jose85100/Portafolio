# 6. Probabilidad: contar, condicionar y actualizar

**Objetivo:** distinguir sucesos, independencia y probabilidad condicional.

## Espacio y sucesos

Un espacio muestral contiene resultados posibles. Un suceso es un conjunto de resultados. En un dado justo, $P(\{2,4,6\})=3/6$. Las probabilidades son no negativas, suman 1 sobre todo el espacio y se suman para sucesos disjuntos.

En general $P(A\cup B)=P(A)+P(B)-P(A\cap B)$: restamos la intersección para no contarla dos veces. Si $P(B)>0$:
$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}.$$
Condicionar cambia el conjunto de referencia.

Independencia significa $P(A\cap B)=P(A)P(B)$. Dos sucesos disjuntos con probabilidad positiva no son independientes: saber que ocurrió uno excluye el otro.

## Bayes y falsas alarmas

Supón 10 000 solicitudes sintéticas: 100 fraudulentas y 9 900 legítimas. Un detector alerta sobre 90 fraudulentas (sensibilidad 90%) y 495 legítimas (tasa de falsos positivos 5%). Entre 585 alertas, solo 90 corresponden a fraude:
$$P(F\mid A)=\frac{0.9(0.01)}{0.9(0.01)+0.05(0.99)}=\frac{2}{13}\approx15.38\%.$$
Una sensibilidad alta no garantiza que una alerta sea fraude. La prevalencia importa. Estos números son hipotéticos, no evidencia de un detector real.

## Variables aleatorias y esperanza

Una variable aleatoria asigna un número a cada resultado. Si $X$ indica incumplimiento, $X\sim\mathrm{Bernoulli}(p)$, $E[X]=p$ y $\mathrm{Var}(X)=p(1-p)$. La esperanza es promedio ponderado, no resultado garantizado.

Con exposición fija 1 000, severidad fija 0.4 y probabilidad 0.05, la pérdida $L=400X$ tiene $E[L]=20$. Si severidad y exposición son aleatorias y dependientes del incumplimiento, no se deben multiplicar promedios sin justificar: la identidad general es $E[L]=P(D)E[\mathrm{LGD}\cdot\mathrm{EAD}\mid D]$ cuando la pérdida es cero fuera del default.

## Ejercicios y soluciones

1. Dos monedas justas independientes: probabilidad de dos caras $1/4$.
2. Si $P(A)=0.4$, $P(B)=0.5$ e independencia, $P(A\cup B)=0.4+0.5-0.2=0.7$.
3. Para Bernoulli con $p=0.2$, varianza $0.16$.
4. ¿$P(F\mid A)=P(A\mid F)$? No: en el ejemplo son 15.38% y 90%, respectivamente.

**Para cuestionarte:** si se reduce la prevalencia manteniendo sensibilidad y falsos positivos, ¿qué pasa con la proporción de fraude entre las alertas? Disminuye; compruébalo sustituyendo 0.001.
