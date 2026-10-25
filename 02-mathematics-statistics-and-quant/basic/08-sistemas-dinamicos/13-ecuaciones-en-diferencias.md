# 13. Ecuaciones en diferencias y estabilidad

**Objetivo:** distinguir equilibrio, trayectoria y estabilidad. Prerrequisitos: sucesiones y funciones. [Notebook](notebooks/08-series-taylor-y-dinamica.ipynb).

## Del estado actual al siguiente

Una recurrencia define $z_{t+1}=a+bz_t$, dado z₀. Un equilibrio z* no cambia: z*=a+bz*. Si b≠1, z*=a/(1-b).

Restar esta igualdad de la recurrencia da $z_{t+1}-z^*=b(z_t-z^*)$. Iterando:
$$z_t=z^*+b^t(z_0-z^*).$$
Esta fórmula describe tanto convergencia como divergencia, no solo el equilibrio.

## Casos de estabilidad

Si |b|<1, la distancia al equilibrio tiende a cero. Con 0<b<1 se aproxima sin cambiar de lado; con -1<b<0 alterna alrededor del equilibrio. Si |b|>1, una perturbación inicial crece. Con b=-1 puede oscilar sin converger. Con b=1, zₜ=z₀+at: si a≠0 no existe equilibrio; si a=0 todo estado es equilibrio.

La estabilidad depende de parámetros y perturbaciones, no de que la ecuación tenga una solución estacionaria.

## Ejemplo de saldo

Si $D_{t+1}=1.02D_t-100$, el equilibrio algebraico es 5000. Pero b=1.02>1: es inestable en el modelo sin restricciones. Desde D₀=4000 el saldo disminuye; desde 6000 aumenta. En un crédito real, pagos finales, mora y límites de saldo cambian la recurrencia. No extrapoles saldos negativos como deudas reales.

## Ejercicios con solución

1. Para zₜ₊₁=2+0.5zₜ y z₀=0, z*=4 y zₜ=4(1-0.5ᵗ).
2. Para zₜ₊₁=2-0.5zₜ, z*=4/3; converge alternando.
3. ¿Un equilibrio siempre atrae? No: el caso b=1.02 lo refuta.
4. Con b=0, ¿cuánto tarda en alcanzar equilibrio? Un paso: z₁=a, independientemente de z₀.

**Siguiente pregunta:** en modelos no lineales, la derivada de la función de transición cerca del equilibrio ayuda a estudiar estabilidad local; no garantiza comportamiento global.

