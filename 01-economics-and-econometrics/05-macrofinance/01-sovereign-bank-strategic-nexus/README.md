# Sovereign–Bank Strategic Nexus

> **Estado: S2 parcial.** [Sovereign Clearing Audit](sovereign-clearing-audit/) implementa un componente estático de balance y pagos interbancarios con tests, LP y oráculo racional. El juego dinámico, los precios endógenos, garantías e identificación empírica siguen S1. No hay resultados empíricos ni teoremas nuevos del programa completo.

## Pregunta de investigación

¿Cómo se amplifica una crisis fiscal mediante las decisiones estratégicas de deuda soberana y liquidez bancaria?

## Hipótesis falsable

H1: exposición soberana, garantías implícitas y ventas forzadas crean retroalimentación no lineal.

## Modelo económico y matemático

Juego dinámico gobierno-bancos-inversionistas con restricción presupuestal y precios de deuda endógenos.

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Event studies de anuncios fiscales, shocks globales e instrumentos de exposición predeterminada.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

Ministerio de Hacienda, Banco de la República, Superfinanciera, BIS, IMF, deuda TES.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Resolver equilibrio, stress de haircut y liquidez, escenarios de intervención; comparar con stress estático.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Endogeneidad fiscal y falta de datos de balance granular limitan identificación.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.

## Ciclo 2026-10-18

[Sovereign Clearing Audit](sovereign-clearing-audit/): primer componente S2 del
programa. Reutiliza el mecanismo EN ya presente en el laboratorio semanal sin
atribuirse su novedad; añade balances soberanos estáticos, contrato de parada,
oráculos y conciliación entre impago bruto y acreedores externos. No implementa
todavía el doom loop fiscal endógeno ni el juego dinámico descrito arriba.
