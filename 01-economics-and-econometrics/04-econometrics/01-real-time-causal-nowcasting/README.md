# Real-Time Causal Nowcasting

> **Estado: S2 parcial — prototipo de evaluación sintética.** [Vintage Audit](vintage-audit/) implementa evaluación as-of con OLS, tests y benchmark. El modelo de factores/MIDAS y la identificación causal siguen en S1; no hay resultados empíricos ni teoremas demostrados.

## Pregunta de investigación

¿Cuánto del error de pronóstico y de atribución causal proviene de revisiones y asincronía informativa?

## Hipótesis falsable

H1: evaluación con vintages reduce sesgo retrospectivo y revela inestabilidad estructural no visible en datos finales.

## Modelo económico y matemático

Factor dinámico de estado-espacio con ragged edge, MIDAS y medición explícita de vintage de publicación.

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Backtesting pseudo-real-time; descomposición de errores por revisión, disponibilidad y shock; placebo temporal.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

DANE, Banco de la República, FRED/ALFRED, IMF; confirmar disponibilidad histórica por vintage.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Kalman, MIDAS, rolling origin, scoring probabilístico y test de Diebold-Mariano con cautela por dependencia.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Vintages incompletos impiden reconstrucción exacta; pronóstico no equivale a identificación causal.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.

## Ciclo 2026-10-12

MVP ejecutable: [Vintage Audit](vintage-audit/). Comando y resultados en su README; alcance sintético y madurez parcial explícitos.
