# Ecuaciones y agenda — proceso de originación

## Estado después de la ampliación

Los notebooks ya ajustan beta-binomial y calibran un máximo de cinco canales independientes. La mezcla heterogénea conjunta, dependencia multicanal general y un modelo causal de error de observación siguen pendientes.

Los notebooks comparan mezcla y contracción de tasas y calibran CUSUM en un horizonte fijo. Detectan desviaciones simuladas del proceso, no intención ni fraude adjudicado.

## 1. Dependencia por lotes y sobredispersión

**Hipótesis.** La varianza binomial subestima variación si solicitudes de un lote comparten condiciones. Una extensión propuesta para tasa común p y correlación intraclase rho es:

$$\operatorname{Var}(O_g)=n_gp(1-p)[1+(n_g-1)\rho].$$

La expresión supone un modelo intercambiable simple; no debe aplicarse sin cambios a mezcla heterogénea de probabilidades o dependencia temporal arbitraria.

**Experimento propuesto.** Simular lotes beta-binomiales con el mismo promedio y rho creciente. Comparar residuos binomiales, escala por sobredispersión y modelo jerárquico. Evaluar alertas falsas, demora y grupos pequeños con el mismo presupuesto de casos.

**Aceptación/refutación.** La supuesta mejora no puede depender de suprimir grupos con cero eventos. Estimar parámetros en referencia histórica y evaluar en otro período. Si el ajuste absorbe un cambio de proceso real como varianza normal, reportar el costo en demora.

## 2. Umbral conjunto para múltiples canales

**Hipótesis.** Reutilizar el umbral de una serie en muchos canales aumenta la probabilidad de alguna alerta. Se propone calibrar el máximo conjunto a horizonte H:

$$P\left(\max_{g\leq G,t\leq H}S_{gt}>h\right)\leq\alpha.$$

Es un objetivo a horizonte fijo, no una garantía de tasa diaria ni control para monitoreo infinito. La dependencia entre canales debe estar representada en la calibración.

**Experimento propuesto.** Comparar G=1/10/50 con correlación de shocks. Calibrar h usando réplicas de referencia y medir falsas alarmas en réplicas distintas. Conservar la demora para varios tamaños de cambio, prealarmas y censura. Repetir después de reinicios y períodos de espera.

**Aceptación/refutación.** Mostrar intervalo de Monte Carlo y no exigir exactamente alpha en una muestra finita. Si solo mejora falsas alarmas porque deja de detectar todos los cambios pequeños, no declarar superioridad global. Seleccionar h en función de costo y capacidad, no por un test elegido retrospectivamente.

## 3. Separar fallo de proceso y fallo de observación

**Hipótesis.** Una omisión observada puede combinar evento real y fallo de registro. Con una variable de calidad Q:

$$P(O=1\mid X)=\sum_{z,q} P(O=1\mid Z=z,X,Q=q)P(Z=z,Q=q\mid X).$$

Z representa estado real del proceso y O su observación. Sin fuentes adicionales, distintas combinaciones pueden producir la misma serie; el notebook CUSUM construye explícitamente esa equivalencia.

**Experimento propuesto.** Simular cambios de política, caídas de logging y omisiones reales con bitácora independiente. Comparar un detector único contra dos canales: calidad y proceso. Medir qué alertas quedan sin atribución y costo de investigación, en vez de forzar todas a una clase.

**Aceptación/refutación.** La atribución necesita evidencia que no derive de la misma señal anómala. Si se usa una etiqueta de causa obtenida después, no convertirla en predictor disponible antes. Conservar estados de evidencia insuficiente, incidente técnico e incumplimiento de proceso antes de hablar de fraude.
