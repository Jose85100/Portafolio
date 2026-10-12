# Bases de Seguros, clima y conducta

**Naturaleza:** fundamentos de la práctica; no es uno de sus siete proyectos. Los siete proyectos están en carpetas hermanas.

## 1. Objeto, alcance y taxonomía

Reservas, peligro climático, transición y daño al consumidor. Definir unidad de análisis, exposición, evento, fecha de observación y disponibilidad, horizonte, actores, decisión y moneda cuando aplique.

## 2. Núcleo matemático

R_0=Σ_t v_t E[C_t|F_0]; hazard λ_i(t|z); pérdida climática L=Σ_i E_i V_i(H_i) con vulnerabilidad V_i dependiente del peligro.

**Trabajo riguroso:** identificar condiciones de existencia, diferenciabilidad, integrabilidad, identificación y estabilidad de cada funcional; demostrar propiedades que se utilicen para decisiones. Separar identidad exacta, aproximación y supuesto empírico.

## 3. Estadística y econometría

Triángulos de desarrollo, GLM, modelos espaciales, EVT, supervivencia y escenarios climáticos.

Para cada estimador especificar estimando, likelihood/momentos, mecanismo de selección, tamaño efectivo, intervalos y diagnósticos. Considerar dependencia temporal/espacial, censura y no estacionariedad según corresponda.

## 4. Métodos numéricos

Construir baseline determinista, simulación o optimización con tolerancias, convergencia, complejidad, control de semillas y análisis de error. Priorizar C++20 para cálculo intensivo, Python para calibración y SQL para preparación point-in-time. No afirmar que estos motores ya existen.

## 5. Riesgos metodológicos

Horizontes largos, no estacionariedad climática, escenarios no probabilísticos, geocodificación y equidad.

## 6. Gobierno y controles

Gobierno actuarial, protección al consumidor, validación de escenarios y divulgaciones aplicables.

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
