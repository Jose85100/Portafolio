# Originación causal y aprobación contrafactual

> **Estado:** prototipo sintético de evaluación de políticas, con propensiones y medias de resultado conocidas; no validado con solicitantes reales ni apto para decisiones de crédito. Línea 1 de siete.

## Experimento reproducible

Se implementó una primera evaluación fuera de política en [src/experiment.py](src/experiment.py), usando solamente la biblioteca estándar de Python. Genera solicitantes independientes con una covariable uniforme, acción binaria de aprobar/rechazar y política histórica conocida con probabilidades entre 0,2 y 0,8. Rechazar produce utilidad cero; la utilidad esperada de aprobar es `0,8 × x − 0,1`, más ruido normal. Estas utilidades son unidades arbitrarias, no pérdidas monetarias estimadas. Se comparan aprobar a todos, rechazar a todos y aprobar cuando `x ≥ 0,125`; sus valores poblacionales verdaderos son, respectivamente, 0,3, 0 y 0,30625.

El evaluador calcula el método directo, ponderación inversa (IPS) y AIPW, además del error estándar de las contribuciones individuales, tamaño de muestra efectivo y peso máximo. Incluye una comparación AIPW pareada frente a tratar siempre, con incertidumbre de la diferencia que conserva la covarianza entre políticas. El experimento usa **propensión y media de resultado verdaderas**, no modelos ajustados; una prueba comprueba que IPS/AIPW recuperan aproximadamente el valor aun si se sustituye la media por cero. La muestra y las políticas se fijan antes de evaluarse; no se selecciona una política sobre la misma muestra. El error estándar supone observaciones independientes y no cubre incertidumbre de modelos estimados. Se rechazan propensiones sin solapamiento; no se recortan pesos silenciosamente.

Desde la raíz del repositorio:

```bash
python3 03-financial-risk/04-advanced-research/01-causal-origination-policy/src/experiment.py
python3 -m unittest discover -s 03-financial-risk/04-advanced-research/01-causal-origination-policy/tests -v
```

La identificación para datos reales exigiría consistencia, ausencia de confusión no medida condicional a las variables disponibles al decidir, positividad y desenlaces comparables para cada acción. La aprobación determina qué resultados de crédito se observan: los resultados de rechazados no se observan y no quedan identificados automáticamente. Faltan modelos de propensión y resultado estimados con separación temporal o cross-fitting, políticas aprendidas fuera de muestra, costos, censura, datos gobernados y análisis de sensibilidad; el ejercicio no demuestra mejora de una política real ni cumple por sí solo requisitos regulatorios.

## Covariable observada con tratamiento simulado

El [experimento semisintético UCI](semisynthetic_uci/) usa cupos observados de tarjetas de Taiwán con asignaciones y utilidades simuladas. Permite contrastar IPS y AIPW contra una verdad conocida, sin afirmar identificación ni desempeño de una política real.

## Pregunta y contribución

**Pregunta:** ¿Cómo estimar el valor causal de aprobar, rechazar o cambiar límite y precio?

**Hipótesis falsable:** el método avanzado produce una mejora de utilidad económica fuera de muestra frente a reglas de negocio y un baseline interpretable, respetando restricciones regulatorias, éticas y operativas. No se presume que la hipótesis sea verdadera.

## Formulación matemática

Esquema formal inicial (la notación y los supuestos deben cerrarse antes de estimar):

```text
V(pi)=E[Y(pi(X))-C(pi(X))]
```

Definir unidad de observación, horizonte, filtración de información, variables de decisión, función de pérdida, restricciones y distribución de perturbaciones. Demostrar propiedades de existencia/identificación cuando correspondan; evaluar sensibilidad ante ruptura de estacionariedad, positividad, independencia y convexidad.

## Modelo estadístico

**Familias candidatas:** AIPW, propensity scores, off-policy doubly robust. Baseline: regresión logística, survival clásico, reglas de negocio o Markov homogéneo según el target. Estimar incertidumbre por bootstrap agrupado a cliente/cohorte o posterior bayesiano; separar entrenamiento, calibración y test temporal. Modelar censura, observaciones repetidas, dependencia entre clientes y cambios de política.

**Datos mínimos:** Aprobaciones, límites, tasas, mora y desempeño por vintage. Documentar granularidad, definiciones de default y cura, fechas de disponibilidad, faltantes, consentimiento, lineage y controles de calidad. Los datos sintéticos son útiles para pruebas, pero no para afirmar rendimiento real.

## Experimento y validación

1. Definir target y población elegible sin información posterior a la fecha de decisión.
2. Construir baseline y especificación avanzada con splits rolling-origin / out-of-time.
3. Comparar calibración, discriminación, incertidumbre y **valor económico incremental** neto de costos.
4. Medir heterogeneidad por vintage, segmento, ciclo macro y canales; hacer ablation y pruebas de drift.
5. Ejecutar stress adverso y reverso, sensitivity analysis y benchmarks contra políticas actuales.
6. Evaluar riesgo de sesgo, robustez, auditabilidad y guardrails antes de recomendar cambios.

**Criterio de éxito:** utilidad incremental positiva con intervalo de incertidumbre y cumplimiento simultáneo de límites; declarar resultados nulos y sensibilidad a supuestos.

## Arquitectura objetivo

```text
src/       -> generador de escenarios, estimación y decisiones
configs/   -> parámetros y escenarios versionados
tests/     -> invariantes, casos límite y pruebas de regresión
notebooks/ -> EDA, calibración, backtesting y ablation
reports/   -> model card, comité y stress results
data/      -> diccionario, licencias y procedencia (sin PII)
```

Esta estructura es una **hoja de ruta**; únicamente `src/experiment.py` y sus pruebas existen para el experimento sintético descrito arriba. Reproducibilidad objetivo: Python, semillas, CI, versionado de datos y parámetros, revisión independiente y control de cambios.

## Impacto de negocio

Traducir resultados a una política accionable: límites de aprobación, apetito, intensidad de cobranza, provisiones, capital o stress según corresponda. Reportar impacto en margen, pérdida esperada, capital, liquidez, recuperación y experiencia del cliente, con escenarios base/adverso/severo.

## Limitaciones y gobierno

Sesgo de selección de rechazados y ausencia de positividad. Añadir documentación de supuestos, fairness, privacidad, revisión humana, monitoreo y plan de reversión. Para IFRS 9 y SIAR, verificar normas aplicables a la entidad y jurisdicción; la investigación no constituye asesoría contable o regulatoria.

## Hitos de investigación

- **M1:** revisión sistemática, DAG/identificación, hipótesis y protocolo.
- **M2:** datos, generador sintético y baseline reproducible.
- **M3:** estimador avanzado y derivación de propiedades.
- **M4:** validación temporal, stress, incertidumbre y benchmark.
- **M5:** model card, reporte ejecutivo, decisión y próximos experimentos.

**Bibliografía a construir:** papers fundacionales de AIPW, propensity scores, off-policy doubly robust, documentación metodológica de backtesting y fuentes normativas primarias según el caso. Registrar DOI, fecha y versión; no citar resultados no verificados.
