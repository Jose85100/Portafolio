# Evidencia empírica de la primera ingesta y benchmark observados

**Ejecución verificada:** [GitHub Actions run 42148509315](https://github.com/Jose85100/Portafolio/actions/runs/42148509315). Trabajo de extracción de datos y benchmark individual finalizados con estado SUCCESS. Las cifras se obtuvieron del log del job, no se estimaron.

## ICETEX: cartera educativa colombiana agregada

- Provider identificado y contrastado: **ICETEX, Vicepresidencia de Crédito y Cobranza**. Catálogo https://www.datos.gov.co/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir
- Fuente: Socrata dataset `dugh-vkir`, series de cartera por fecha, departamento, etapa Estudios/Amortización.
- **1.308** registros de la fuente en ejecución, **1.240** aceptados, **68** rechazados (**5,1988%**).
- Artefacto: `observed-colombia-credit-snapshot` (ID 13471306282) con CSV, manifiesto hash y rechazos.
- La validación estricta del primer intento falló en conciliación y el código se actualizó para cuarentena con umbral técnico provisional del 10%.
- **IMPORTANTE:** El éxito de publicación no significa que 68 errores sean aceptables para MRM o IFRS 9. Su causa debe analizarse individualmente. No deben rellenarse ni asumirse valores correctos.
- Datos observados agregados de ICETEX, no de la SFC ni del sistema financiero completo. Son prevalencias de stock y no PD 12 meses ni transiciones de default.

## UCI credit cards (observado individual, Taiwán 2005)

- Origen: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients+dataset
- Licencia CC BY 4.0. DOI 10.24432/C55S3H.
- 30.000 individuos, 22.500 entrenamiento / 7.500 test estratificado aleatorio.
- Modelo: regresión logística escalada con imputación; sin variables demográficas sensibles.
- **AUC = 0,7141968618; Gini = 0,4283937236; KS = 0,3760144121; Brier = 0,1460696930.**
- Artefacto: `observed-uci-pd-benchmark` (ID 13470444530).
- Target: incumplimiento **del siguiente mes**, no default 12 meses, ni lifetime IFRS 9.
- El holdout **no es OOT**. La muestra no es representativa de deudores colombianos. No se afirma validez productiva ni calibración por población.

## Estado de integración

1. **Completado y ejecutado:** fuente real ICETEX -> descarga -> validación/filtrado explícito -> CSV + manifest + artefacto de CI.
2. **Completado y ejecutado:** UCI -> microdatos observados -> regresión logística -> métricas reales -> artefacto de CI.
3. **Verificado en [run 42148884390](https://github.com/Jose85100/Portafolio/actions/runs/42148884390):** 19 periodos observados y 56 filas de señales de mora >90 días ponderadas por número de créditos, separadas por etapa y total; cuatro pruebas nuevas. Las 68 exclusiones corresponden a **fallas de conciliación de conteos**, documentadas en cuarentena. El archivo de señales está disponible como artefacto temporal de esa ejecución.
4. **Pendiente:** versionado persistente de datasets brutos y publicaciones, SQL/Spark, join point-in-time al motor IFRS 9, etiquetas nacionales PD/LGD/EAD, calibración y aprobación independiente.

**No convertir el dataset del ICETEX en etiqueta individual de PD.** No deben sumarse porcentajes regionales sin usar sus denominadores de crédito. Conservar explícitamente `epoca_cartera` y fechas de publicación.
