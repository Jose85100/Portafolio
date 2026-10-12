# Tiempo estocástico de recuperación

**Práctica:** Riesgo operacional y resiliencia  
**Madurez:** S1, diseño científico y de producto; no implementación, resultados, ni conformidad regulatoria.

## 1. Mandato y pregunta falsable

¿Qué controles reducen cuantiles altos del tiempo de recuperación?

**Hipótesis:** una metodología específica supera un baseline previamente establecido en una métrica apropiada sin degradación inadmisible de estabilidad, calibración o costo. Definir métrica y umbral antes de evaluar.

## 2. Formulación matemática

T_rec=min{t:X_t∈estado operativo}; supervivencia S(t)=P(T_rec>t).

**Obligaciones teóricas:** especificar variables y unidades, espacios de probabilidad, información temporal, supuestos, condiciones de existencia e identificabilidad, demostraciones cuando corresponda y contraejemplos. Las expresiones son esquemas de modelado que requieren formalización por caso.

## 3. Modelado estadístico

Modelos de duración censurada, hazards y escenarios.

Documentar estimando, sesgo de selección, incertidumbre paramétrica y de escenario, intervalos y pruebas de sensibilidad. No inferir causalidad únicamente de correlación.

## 4. Arquitectura computacional

C++ Monte Carlo; Python supervivencia; SQL cronología de incidentes.

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
