# Reverse stress del apetito de riesgo

**Práctica:** Gobierno, ERM y estrategia  
**Madurez:** S1, diseño científico y de producto; no implementación, resultados, ni conformidad regulatoria.

## 1. Mandato y pregunta falsable

¿Qué perturbación mínima causa incumplimiento del apetito?

**Hipótesis:** una metodología específica supera un baseline previamente establecido en una métrica apropiada sin degradación inadmisible de estabilidad, calibración o costo. Definir métrica y umbral antes de evaluar.

## 2. Formulación matemática

min_z ||z−z0||_W sujeto a g(z)≥límite; programación no convexa.

**Obligaciones teóricas:** especificar variables y unidades, espacios de probabilidad, información temporal, supuestos, condiciones de existencia e identificabilidad, demostraciones cuando corresponda y contraejemplos. Las expresiones son esquemas de modelado que requieren formalización por caso.

## 3. Modelado estadístico

Calibrar escenarios plausibles y cuantificar incertidumbre de frontera.

Documentar estimando, sesgo de selección, incertidumbre paramétrica y de escenario, intervalos y pruebas de sensibilidad. No inferir causalidad únicamente de correlación.

## 4. Arquitectura computacional

C++ optimizador; Python escenarios; SQL límites.

**Diseño futuro (no implementado):** `cpp/include/`, `cpp/tests/`, `python/src/`, `python/tests/`, `sql/`, `experiments/`, `docs/`. Los contratos de entradas/salidas serán versionados y usarán datos sintéticos para tests.

## 5. Experimentos y validación

1. Baseline explícito y caso sintético con verdad conocida.
2. Pruebas de invariantes, unidades, límites, datos inválidos y casos extremos.
3. Simulaciones Monte Carlo o optimización con error numérico y criterios de convergencia.
4. Validación temporal, por segmentos o por escenarios, según naturaleza del estimando.
5. Robustez frente a cambios de régimen, dependencia y errores de especificación.
6. Reportar tiempo, memoria, semillas, versiones y reproducibilidad.
7. Revisión independiente, interpretación económica, riesgos de uso y restricciones regulatorias.

## 6. Evidencia, decisiones y entregables

D1 diagnóstico; D2 metodología; D3 código y pruebas; D4 validación independiente; D5 implementación y controles; D6 reporte ejecutivo. D3–D6 son **pendientes**, no entregables ya producidos.

## 7. Restricciones y gobierno

Los datos sintéticos validan cálculos, no desempeño real. Verificar regulación por jurisdicción y tipo de entidad; no confundir capital económico, regulatorio y contable. Seguir [arquitectura transversal](../../00-architecture/README.md).


## Aplicación con datos observados y supuestos

[Notebook reproducible](aplicacion-datos-observados.ipynb). Usa datos públicos y documenta los supuestos y límites; no acredita validación institucional. Requiere Python, pandas, matplotlib, Jupyter y un clon del repositorio.


**Robustez del notebook:** Incluye sensibilidad por presupuesto y proporción de deuda que reprecia; las frecuencias históricas usan ventanas solapadas.


## Literatura y variantes aplicadas

El notebook compara ventanas anuales diciembre a diciembre no solapadas y resume superaciones históricas. Referencia: [FSB/BCBS, Stress Testing Principles (2018)](https://www.fsb.org/2018/10/stress-testing-principles/). Las frecuencias no son probabilidades futuras ni un escenario de inviabilidad institucional.
