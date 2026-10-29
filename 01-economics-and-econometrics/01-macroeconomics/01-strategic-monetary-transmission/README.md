# Strategic Monetary Transmission

> **Estado del programa: formulación (S1).** El benchmark `inflation-bias-audit` aporta un componente lineal-cuadrático S2 local; no implementa todavía el juego de Markov heterogéneo del programa ni proporciona resultados empíricos.

## Pregunta de investigación

¿Cómo altera la anticipación estratégica de bancos, hogares y empresas la transmisión de un shock monetario?

## Hipótesis falsable

H1: la complementariedad de decisiones de crédito e inversión modifica no linealmente las respuestas agregadas, condicionadas por liquidez y heterogeneidad.

## Modelo económico y matemático

Juego dinámico estocástico de Markov con agentes heterogéneos y banco central; políticas de equilibrio mediante ecuaciones de Bellman.

Se debe especificar formalmente el conjunto de agentes \(i\in\mathcal I\), el estado \(s_t\), el conjunto de información \(\mathcal F_{i,t}\), las acciones \(a_{i,t}\), las restricciones \(g_i(s_t,a_t)\leq0\), las utilidades \(u_i\) y la ley de transición \(P(s_{t+1}\mid s_t,a_t)\). Para problemas dinámicos, comenzar por

\[
V_i(s)=\max_{a_i\in A_i(s)}\left\{u_i(s,a_i,a_{-i}^*(s))+\beta_i\,\mathbb E[V_i(s')\mid s,a_i,a_{-i}^*(s)]\right\}.
\]

Esta ecuación es un **marco general**, no una demostración de existencia de equilibrio para el caso. La prueba deberá declarar compacidad, continuidad, condiciones de contracción/convexidad o estrategias mixtas cuando corresponda. Documentar contraejemplos al relajar supuestos.

## Identificación econométrica

Identificación de shocks monetarios externos, proyecciones locales con heterogeneidad y contraste estructural de respuestas.

Declarar estimando, conjunto de información, DAG o estructura causal, supuestos de exclusión/exogeneidad, errores de medición y análisis de identificación parcial si los datos no permiten identificación puntual.

## Datos públicos potenciales

Banco de la República (tasas, ISE), DANE (PIB, empleo), BIS/IMF; verificar cobertura y fechas de publicación.

Antes de la ejecución: registrar URL oficial, licencia, frecuencia, geografía, cobertura, fecha de observación, fecha de publicación, revisiones y hash de cada archivo. La disponibilidad efectiva **no ha sido verificada**.

## Algoritmos y simulación

Solución de equilibrio, shocks impulso-respuesta, sensibilidad a fricciones y expectativas; comparar con VAR/LP no estratégicos.

Protocolo mínimo: baseline analítico, semillas fijadas, sensibilidad de parámetros, convergencia de malla/solver, tests de invariantes, incertidumbre por bootstrap o Monte Carlo y costo computacional. Separar calibración de estimación e identificación.

## Validación y contribución

- Formular una predicción observable que diferencie el mecanismo de al menos dos hipótesis rivales.
- Reportar falsaciones, controles negativos, estabilidad temporal, escenarios y limitaciones.
- Revisar sistemáticamente literatura para delimitar contribución original; no afirmar prioridad científica sin evidencia.
- Publicar ecuaciones, supuestos, código, metadatos, resultados y registro de cambios reproducibles.

## Riesgos y límites

Equilibrios múltiples, problemas de identificación y observación limitada de expectativas.

## Ruta de implementación

1. Revisión sistemática y pregunta identificable.
2. Modelo formal, proposiciones y demostraciones o contraejemplos.
3. Dataset versionado, contratos y vintages.
4. Solver/estimador, simulación y pruebas automatizadas.
5. Backtesting, análisis de robustez y reporte reproducible.


## Componente S2: expectativas y compromiso

[inflation-bias-audit](inflation-bias-audit/) contrasta compromiso contingente y discreción con expectativas racionales. Una alternativa con menor pérdida aparente se rechaza por expectativas inconsistentes. Es un benchmark estático previo, no una validación de la hipótesis principal sobre liquidez, inversión y heterogeneidad.
