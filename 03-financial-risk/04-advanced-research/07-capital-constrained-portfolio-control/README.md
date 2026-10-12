# Optimización de portafolio con capital y provisiones

> **Estado: propuesta de investigación; no implementado ni validado.** Línea 7 de siete.

## Pregunta y contribución

**Pregunta:** ¿Cómo asignar originación, pricing y límites maximizando valor sujeto a ECL y capital?

**Hipótesis falsable:** el método avanzado produce una mejora de utilidad económica fuera de muestra frente a reglas de negocio y un baseline interpretable, respetando restricciones regulatorias, éticas y operativas. No se presume que la hipótesis sea verdadera.

## Formulación matemática

Esquema formal inicial (la notación y los supuestos deben cerrarse antes de estimar):

```text
max_x E[NPV(x)]-lambda*CVaR_alpha(L(x)); s.t. ECL(x)<=B, Capital(x)<=K
```

Definir unidad de observación, horizonte, filtración de información, variables de decisión, función de pérdida, restricciones y distribución de perturbaciones. Demostrar propiedades de existencia/identificación cuando correspondan; evaluar sensibilidad ante ruptura de estacionariedad, positividad, independencia y convexidad.

## Modelo estadístico

**Familias candidatas:** Programación estocástica, CVaR, optimización robusta. Baseline: regresión logística, survival clásico, reglas de negocio o Markov homogéneo según el target. Estimar incertidumbre por bootstrap agrupado a cliente/cohorte o posterior bayesiano; separar entrenamiento, calibración y test temporal. Modelar censura, observaciones repetidas, dependencia entre clientes y cambios de política.

**Datos mínimos:** PD/LGD/EAD, margen, demanda, fondeo, capital, costos. Documentar granularidad, definiciones de default y cura, fechas de disponibilidad, faltantes, consentimiento, lineage y controles de calidad. Los datos sintéticos son útiles para pruebas, pero no para afirmar rendimiento real.

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

Esta estructura es una **hoja de ruta**, no archivos creados en este commit. Reproducibilidad: Python, semillas, CI, versionado de datos y parámetros, revisión independiente y control de cambios.

## Impacto de negocio

Traducir resultados a una política accionable: límites de aprobación, apetito, intensidad de cobranza, provisiones, capital o stress según corresponda. Reportar impacto en margen, pérdida esperada, capital, liquidez, recuperación y experiencia del cliente, con escenarios base/adverso/severo.

## Limitaciones y gobierno

Errores de predicción amplificados por optimización. Añadir documentación de supuestos, fairness, privacidad, revisión humana, monitoreo y plan de reversión. Para IFRS 9 y SIAR, verificar normas aplicables a la entidad y jurisdicción; la investigación no constituye asesoría contable o regulatoria.

## Hitos de investigación

- **M1:** revisión sistemática, DAG/identificación, hipótesis y protocolo.
- **M2:** datos, generador sintético y baseline reproducible.
- **M3:** estimador avanzado y derivación de propiedades.
- **M4:** validación temporal, stress, incertidumbre y benchmark.
- **M5:** model card, reporte ejecutivo, decisión y próximos experimentos.

**Bibliografía a construir:** papers fundacionales de Programación estocástica, CVaR, optimización robusta, documentación metodológica de backtesting y fuentes normativas primarias según el caso. Registrar DOI, fecha y versión; no citar resultados no verificados.
