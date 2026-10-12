# 05. Validación independiente, backtesting y gobierno de modelos IFRS 9

## 1. Tres niveles de validación

**Conceptual:** el objeto estadístico coincide con el objeto contable; horizontes, definiciones, descuento, flujos y stages están alineados. **Estadística:** estimadores calibrados, discriminantes, estables y sin filtración de información. **Operativa:** reproducibilidad, integridad de datos, controles de cambios, conciliación contable, permisos y evidencia de ejecución. Aprobar una prueba de AUC no valida ECL.

## 2. Diseño de muestras y temporalidad

Definir fecha as-of \(t\), horizonte \(H\), ventana de maduración y calendario de observación. Separar entrenamiento, validación y prueba **por tiempo**, no por filas aleatorias, para reducir leakage entre observaciones repetidas del mismo crédito. Considerar agrupación por deudor y cohortes. Un contrato observado en múltiples meses no genera observaciones independientes; intervalos ingenuos subestiman incertidumbre.

En validación retrospectiva, la predicción debe reconstruirse con datos y escenarios realmente disponibles en \(t\). Documentar derechos de censura: contratos con resultado no maduro no deben tratarse automáticamente como no-default.

## 3. Backtesting de PD

Para \(n\) exposiciones con PD \(p_i\), el número esperado de defaults es \(\mu=\sum p_i\). Si se asume independencia condicional, \(\operatorname{Var}(D)=\sum p_i(1-p_i)\); con dependencia, agregar \(2\sum_{i<j}\operatorname{Cov}(D_i,D_j)\). Un z-test binomial simple sobre una cartera correlacionada puede producir falsos rechazos.

Usar calibración por horizonte y producto, Brier score \(n^{-1}\sum(y_i-p_i)^2\), log-loss, curvas de calibración y bandas de incertidumbre. Para hazard, evaluar tanto supervivencia como incidencia acumulada con tratamiento de censura. La discriminación (AUC) no reemplaza calibración.

## 4. Backtesting de LGD y EAD

**LGD:** comparación de valor presente de recuperaciones predichas frente a observadas; segmentación por garantía, vintage de default y tiempo de recuperación; separar casos cerrados y abiertos; intervalos por cohortes. **EAD:** comparar proyección al default desde \(t\) contra saldo realizado en \(\tau\); reportar error por horizonte y tipo de producto. **ECL:** comparar pérdidas realizadas maduras con pronósticos de la misma población y horizonte, reconociendo que las pérdidas contables y realizadas no se alinean necesariamente en calendario de caja sin ajuste.

Una reconciliación agregada favorable puede ocultar compensaciones entre PD subestimada y LGD sobreestimada; validar componentes y producto conjunto.

## 5. Validación SICR

Medir sensibilidad y oportunidad de transferencias Stage 1→2 antes de default, tasas de reversión, estabilidad por vintage, proporción de cartera en Stage 2, sesgos por edad y cambios en macro. La matriz de transición entre stages es una herramienta de seguimiento, no una prueba suficiente de adecuación. Examinar especialmente créditos que entran en default desde Stage 1 sin señal previa y créditos que permanecen mucho tiempo en Stage 2 sin deterioro.

## 6. Validación de escenarios y overlays

Reconstruir vintages macro, medir errores de pronóstico y recalcular ECL con escenarios alternativos. Documentar sensibilidad a pesos, elasticidades y cambios estructurales. Los overlays requieren evidencia del riesgo no capturado, estimación independiente de magnitud, responsable, fecha de expiración y plan para incorporarlo al modelo o retirarlo.

## 7. Indicadores y umbrales de seguimiento

Diseñar tablero con: PD prevista vs observada, LGD descontada prevista vs realizada, EAD prevista vs realizada, ECL por etapa, cobertura, roll rates, migraciones SICR, estabilidad de variables, errores de fuentes y ajustes manuales. Los umbrales deben derivarse de materialidad, tolerancia a riesgo de modelo y variabilidad estadística; no adoptar valores universales arbitrarios de PSI o AUC.

## 8. Gobierno y reproducibilidad

Cada corrida produce manifiesto: commit SHA, versión de datos, corte, población, exclusiones, esquema, parámetros, escenarios, hashes de insumos, resultados, pruebas, aprobaciones y conciliación al libro mayor. Separar desarrollo, validación independiente, aprobación y despliegue. Mantener registro de excepciones, hallazgos y remediaciones.

## 9. Matriz de pruebas mínimas

| Prueba | Resultado esperado | Severidad si falla |
|---|---|---|
| Hazards y PD marginales | En [0,1]; suma ≤ 1 | Crítica |
| Pesos de escenarios | No negativos; suma 1 | Crítica |
| Causalidad temporal | Sin variables publicadas después de as-of | Crítica |
| Cash shortfalls | Conciliación con parametrización | Crítica |
| Descuento | Tasa y fecha coherentes; no duplicación | Alta |
| EAD observada | Solo como etiqueta para validación | Alta |
| PD calibrada por vintage | Intervalos y desviaciones explicadas | Alta |
| SICR | Comparación de riesgo y reglas cualitativas documentadas | Alta |
| Recuperaciones abiertas | Tratamiento explícito de censura | Alta |
| Cambios de modelo | Revisión, aprobación y versionado | Alta |

## 10. Límites de inferencia

No declarar consistencia, insesgadez ni eficiencia de un estimador sin identificar población, mecanismo de muestreo, condiciones de censura y dependencia. Un modelo entrenado con datos sintéticos puede demostrar corrección computacional, pero no desempeño sobre una cartera colombiana real. La validación de cumplimiento requiere revisión de política contable y evidencia específica de la entidad.
