# Climate Adaptation Coordination Games

> **Estado: formulación de investigación.** No se han estimado modelos, demostrado teoremas específicos ni obtenido resultados empíricos en este directorio.

## Pregunta de investigación

¿Por qué inversión privada y pública en adaptación climática puede quedar por debajo del óptimo social?

## Hipótesis falsable

H1: externalidades, riesgo correlacionado y compromisos no creíbles inducen subinversión.

## Modelo económico y matemático

Juego estocástico de inversión entre gobierno, hogares y firmas con daños climáticos y subsidios.

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Evaluar shocks climáticos exógenos condicionados por geografía, tendencias y adaptación previa.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

IDEAM, DANE, UNDRR, EM-DAT y presupuestos abiertos; validar licencias y cobertura.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Equilibrios no cooperativos vs planificador, análisis de sensibilidad, stress climático y valor de coordinación.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Estimación de daños y descuento intertemporal con alta incertidumbre.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.
