# Bases de Riesgo operacional y resiliencia

**Naturaleza:** fundamentos de la práctica; no es uno de sus siete proyectos. Los siete proyectos están en carpetas hermanas.

## 1. Objeto, alcance y taxonomía

Eventos, severidad, continuidad, terceros y recuperación. Definir unidad de análisis, exposición, evento, fecha de observación y disponibilidad, horizonte, actores, decisión y moneda cuando aplique.

## 2. Núcleo matemático

L_T=Σ_{j=1}^{N_T}S_j; si N independiente de severidades iid, E[L_T]=E[N_T]E[S]; S_rec(t)=P(T_rec>t).

**Trabajo riguroso:** identificar condiciones de existencia, diferenciabilidad, integrabilidad, identificación y estabilidad de cada funcional; demostrar propiedades que se utilicen para decisiones. Separar identidad exacta, aproximación y supuesto empírico.

## 3. Estadística y econometría

Poisson/negativo binomial, lognormal/GPD, modelos de supervivencia censurada, simulación de redes y evaluación causal de controles.

Para cada estimador especificar estimando, likelihood/momentos, mecanismo de selección, tamaño efectivo, intervalos y diagnósticos. Considerar dependencia temporal/espacial, censura y no estacionariedad según corresponda.

## 4. Métodos numéricos

Construir baseline determinista, simulación o optimización con tolerancias, convergencia, complejidad, control de semillas y análisis de error. Priorizar C++20 para cálculo intensivo, Python para calibración y SQL para preparación point-in-time. No afirmar que estos motores ya existen.

## 5. Riesgos metodológicos

Sesgo de reporte, truncamiento por umbral, colas extremas, eventos no monetarios y dependencia de proveedores.

## 6. Gobierno y controles

BCP, BIA, RTO/RPO definidos, incident response y pruebas de recuperación con evidencia.

## 7. Contratos y trazabilidad

Usar RunContext/v1, RiskObservation/v1, Scenario/v1, RiskEstimate/v1 y ValidationReport/v1 del [marco transversal](../../00-foundations/). Versionar inputs, supuestos, fuentes, escenario, unidad y resultados; registrar decisiones y revisiones.

## 8. Ruta de validación

S1 especificación → S2 código y tests → S3 simulaciones y benchmarks → S4 validación independiente → S5 operación gobernada. Evaluar baselines, casos límite, robustez, sensibilidad, sesgo y evidencia por separado.

## 9. Proyectos asociados

Consultar [catálogo de los siete proyectos](../README.md). Las bases no cuentan como un octavo proyecto.

## Tres módulos de fundamentación separados

1. [Fundamento matemático y teórico](01-mathematical-and-theoretical-foundations.md)
2. [Fundamento estadístico y econométrico](02-statistical-and-econometric-foundations.md)
3. [Fundamento computacional y numérico](03-computational-and-numerical-foundations.md)

**Conteo:** tres fundamentos y siete proyectos independientes por temática.
