# Resultado observado — mezcla de calificación por producto

Corte más reciente: **2026-08-31**. Ventana disponible: 2015-01-31 a 2026-08-31.

El indicador principal es participación del saldo calificado D+E dentro del saldo calificado A–E. Se muestra junto a la cobertura A–E respecto del saldo bruto para hacer visible el denominador faltante.

## Cortes seleccionados

| Producto | D+E / saldo A–E (%) | Cobertura A–E / bruto (%) | Cambio interanual (pp) | Entidades reportantes |
|---|---:|---:|---:|---:|
| CRÉDITO ROTATIVO | 4.54 | 100.00 | -0.43 | 18 |
| LIBRE INVERSIÓN | 6.88 | 99.15 | -1.93 | 38 |
| MICROCREDITOS < O IGUALES A 25 SMMLV | 5.78 | 98.34 | -0.87 | 24 |
| CARTERA COMERCIAL PYMES | 9.85 | 100.00 | -0.80 | 35 |

## Calidad y lectura

- El archivo de entrada tiene 112,602 filas y 36,147,754 bytes; el filtro `renglon=5` conserva 87,859 totales de producto.
- La llave de detalle `fecha_corte, tipo_entidad, codigo_entidad, unicap, renglon` no tiene filas duplicadas en este vintage; el derivado contiene 4,480 filas únicas en grano mes × producto, 32 productos y 140 cortes.
- 86.05% de las observaciones producto-mes tienen cobertura A–E entre 98% y 102%. Hay 1,198 filas entidad-producto-mes con saldo bruto cero, excluidas de la interpretación de cobertura (no se eliminan del derivado).
- La figura limita la lectura a cuatro productos con cobertura histórica mínima de 95%; sigue mostrando cobertura en el eje derecho. La selección no vuelve comparables las modalidades.
- Los datos están agregados por entidad, modalidad/producto y corte; no contienen observaciones longitudinales de créditos individuales.

## Interpretación y límites

La serie sirve como **proxy descriptivo de mezcla de saldos clasificados en D/E** dentro de cada producto. Se puede usar para exploración, vigilancia sectorial y formular preguntas de análisis más detallado. Cambios pueden reflejar riesgo subyacente, pero también cambios de entidades reportantes, composición de cartera, reglas de calificación o cobertura.

No mide probabilidad de incumplimiento, migraciones A→E, roll-rates, pérdida, mora contractual ni suficiencia de provisiones. No valida una PD de originación ni alimenta decisiones de aprobación, precio, límite o provisión. La ausencia de ID de crédito impide construir transiciones: dos cortes agregados no identifican quién migró de categoría.

Los saldos D/E y A–E se agregan entre reportantes antes de calcular la proporción. En consecuencia, el cambio en la participación de entidades puede alterar el indicador. No se interpreta una diferencia entre productos como una diferencia de riesgo calibrada; sus poblaciones, escalas y prácticas de calificación pueden variar.

## Integridad y linaje

- Dataset oficial SFC `rvii-eis8`; vintage descargado 2026-11-11T01:58:12+00:00 UTC, última actualización de metadata observada 2026-10-23T14:57:52Z (metadata observed 2026-11-10).
- SHA-256 del CSV exacto de entrada: `94e767a38e182ca9a6b0d188eea1617be2afe061ed6841c97e523c6d0168fa2d`. El hash identifica el archivo usado en este build; el snapshot comprimido canónico de Drive queda referenciado por ID `1FcdcUTlIHhV92TN8pEikcz0DX0896HBW` y no se afirma igualdad byte a byte.
- SHA-256 del derivado agregado: `45c116db15aac1912ebf17d6fa4ce69ed328a4a3f71be00d440fcf5d0d782690` (1,101,609 bytes).
- El script valida columnas requeridas, fechas, saldos numéricos, llave entidad×producto×corte y unicidad mes×producto. Los datos crudos permanecen en Drive; este repositorio guarda el derivado agregado.

El informe y la figura son descriptivos. Consultar `manifest.json` para métricas completas de calidad y transformación.
