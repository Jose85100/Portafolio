# Endogenous Credit Freeze

> **Estado: S2 parcial.** [Bayesian Freeze Audit](bayesian-freeze-audit/) implementa un juego bayesiano finito de dos prestamistas con tests, oracle y benchmark. El juego global continuo y la identificación empírica siguen en S1; no hay resultados empíricos.

## Pregunta de investigación

¿Puede producirse una congelación del crédito por coordinación pesimista sin colapso inicial de fundamentales?

## Hipótesis falsable

H1: señales privadas ruidosas y complementariedad de renovación generan umbrales estratégicos y discontinuidades de crédito.

## Modelo económico y matemático

Global game bayesiano con señales privadas, decisión de renovación y equilibrio de umbral.

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Contrastar co-movimiento residual de oferta con shocks fundamentales, exposición a liquidez y redes; evitar equiparar correlación a coordinación.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

Banco de la República, Superfinanciera, BIS y series agregadas bancarias; microdatos sujetos a acceso.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Derivar umbrales, demostrar existencia bajo supuestos, solver de punto fijo, contrafactuales de garantías y transparencia.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Datos agregados pueden no identificar creencias privadas ni coordinación; hipótesis alternativa: shocks comunes.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.

## Ciclo 2026-10-13

Prototipo ejecutable: [Bayesian Freeze Audit](bayesian-freeze-audit/). Enumera todos los perfiles puros del juego finito, reporta multiplicidad y compara con un único punto fijo de mejores respuestas.

## Ciclo 2026-10-14

[Mixed Freeze Audit](mixed-equilibrium-audit/) amplía el componente S2 a estrategias
mixtas de comportamiento: 81 soportes, oráculo racional y rechazo explícito de
soportes singulares factibles. No se eleva la madurez del juego global completo.

## Ciclo 2026-10-15

[Polyhedral Freeze Audit](polyhedral-freeze-audit/) representa también las regiones
degeneradas mediante restricciones/vértices racionales y dimensión afín exacta.
Distingue familias positivas de puntos aislados con soportes singulares; extensión
S2 del mismo juego finito, no solver global ni validación empírica.
