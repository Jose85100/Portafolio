# 06. Caso integrado, descomposición y agenda experimental

## 1. Experimento determinista: crédito de tres años

Supóngase EAD constante 100, LGD condicional 40% ya expresada en valor presente a la fecha de medición, sin prepago y tres hazards anuales \(h=(0.02,0.03,0.04)\). Las PD marginales son:

\[
q_1=0.02,\quad q_2=(0.98)(0.03)=0.0294,\quad
q_3=(0.98)(0.97)(0.04)=0.038024.
\]

Su suma es \(0.087424\), igual a \(1-(0.98)(0.97)(0.96)\). Con LGD descontada fija, ECL de vida = \(100(0.4)(0.087424)=3.49696\). ECL correspondiente a defaults del primer año = \(100(0.4)(0.02)=0.8\). Si LGD no estuviera descontada, habría que introducir calendario y factores de descuento coherentes; este ejemplo **no** permite omitirlos en un modelo real.

El contraste ilustra por qué sumar hazards \(0.02+0.03+0.04=0.09\) sobreestima PD acumulada: ignora la supervivencia previa.

## 2. Ejemplo de escenarios

Para tres escenarios con pesos \((0.2,0.6,0.2)\) y ECL condicional \((6,3,12)\), el promedio ponderado es \(0.2(6)+0.6(3)+0.2(12)=5.4\). El escenario central por sí solo da 3. El ejemplo no implica que pesos o niveles sean adecuados para una entidad particular.

## 3. Agenda experimental y correspondencia con implementación

**A — PD dinámica:** generar cohortes sintéticas con hazard conocida y censura; comparar logit discreto, modelo de supervivencia y gradient boosting con calibración. Criterio: recuperación de parámetros o probabilidades dentro de bandas de Monte Carlo.

**B — SICR:** generar rating al origen y evolución de riesgo; comparar reglas de razón, diferencia absoluta y clasificación híbrida; medir anticipación, falsos positivos y dependencia de antigüedad.

**C — EAD:** simular amortización, utilización y prepago; comparar saldo proyectado, CCF y promedio histórico. No usar saldo futuro como predictor. Evaluar error fuera de tiempo y por horizonte.

**D — LGD:** simular recuperaciones tardías, censura y garantías; comparar promedio de casos cerrados contra modelo de supervivencia de recuperación. Medir sesgo y error descontado.

**E — Dependencia:** simular shocks macro comunes sobre PD, LGD y EAD; medir diferencia entre esperanza del producto y producto de esperanzas. Reportar error de Monte Carlo y sensibilidad a correlación.

**F — Escenarios:** estimar ECL bajo integración Monte Carlo y cuadratura discreta; analizar error por número de escenarios, colas y no linealidad.

**G — Reconciliación:** construir contratos sintéticos con calendarios completos; exigir igualdad entre valoración directa de cash shortfalls y cálculo por componentes cuando ambos representen idénticos supuestos.

## 4. Criterios de aceptación

No aprobar una extensión por tener gráficos convincentes. Exigir pruebas de invariantes, resultados reproducibles, validación temporal, intervalos de incertidumbre, sensibilidad a hipótesis, análisis de fallos y documentación de límites. Los resultados cuantitativos deberán calcularse desde scripts/notebooks y no copiarse manualmente al texto.

## 5. Extensiones de investigación

- Modelos bayesianos jerárquicos para segmentos con pocos defaults.
- Riesgos competitivos de default, prepago y modificación.
- Modelos multiestado para mora, curación, default y recuperación.
- Modelos macro de parámetros variables en el tiempo y cambios de régimen.
- Inferencia causal para evaluar políticas de cobranza sin confundir intervención con selección.
- Conformal prediction y bandas de riesgo: examinar cuidadosamente límites de cobertura bajo dependencia temporal.
- Pruebas de robustez ante rupturas estructurales, deterioro de datos y revisiones macro.

## 6. Qué se puede afirmar

Las identidades de supervivencia y expectativa son demostraciones matemáticas. Los ejemplos numéricos son ejercicios sintéticos verificables. Ninguna conclusión de mejora predictiva, reducción de provisiones o cumplimiento IFRS 9 puede inferirse sin ejecutar experimentos, calibrar sobre datos pertinentes y someter el marco a revisión contable y de riesgo independiente.

## 7. Implementación multimodelo disponible

Los experimentos de PD, EAD, LGD, sensibilidad de escenarios y reconciliación ahora tienen implementaciones parciales y explícitas en `src/multimodel` y notebooks 01–04. Ver [fichas de modelo](docs/MODEL_CARDS.md). No se implementaron gradient boosting, riesgos competitivos, supervivencia de recuperaciones abiertas ni integración Monte Carlo de escenarios. El estado de la agenda se distingue del código ejecutado.
