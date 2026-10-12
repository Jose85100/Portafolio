# Mechanism Design for Financial Inclusion

> **Estado: formulación de investigación.** No se han estimado modelos, demostrado teoremas específicos ni obtenido resultados empíricos en este directorio.

## Pregunta de investigación

¿Qué contratos de financiación inducen revelación de información y pagos sostenibles con ventas inciertas?

## Hipótesis falsable

H1: contratos contingentes al flujo mejoran bienestar y recuperación frente a pagos fijos bajo restricciones de incentivos.

## Modelo económico y matemático

Modelo principal-agente con tipo privado, riesgo moral y restricciones de participación e incentivos (IC/IR).

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Estimar demanda y selección con variación exógena cuando exista; con datos públicos solo calibración y simulación explícitamente etiquetadas.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

Encuestas empresariales DANE, Banca de las Oportunidades, Superfinanciera, Banco Mundial Enterprise Surveys.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Resolver contratos óptimos por tipo, frontera eficiencia-equidad y robustez a subdeclaración y shocks de caja.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Sin microdatos de contratos y resultados, no afirmar efectividad causal en originación real.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.
