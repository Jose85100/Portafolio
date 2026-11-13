# Proxy de calidad de cartera por modalidad — fuente SFC

**Edición observada de referencia:** Indicador de Calidad de Cartera por Vencimiento (ICV) reportado por la Superintendencia Financiera de Colombia. **No es una PD, etiqueta de default individual, ni matriz de migración.** El laboratorio de scorecards, cosechas y transiciones del proyecto vecino conserva sus datos controlados.

## Pregunta y decisión

¿Qué modalidades presentan niveles o deterioros relativos de cartera vencida que ameriten priorizar revisión de exposición, originación reciente o políticas de cobranza? La serie permite comparar señales agregadas y dispersiones entre entidades; no permite atribuir el cambio a comportamiento de las mismas operaciones ni inferir una probabilidad de incumplimiento.

## Proxy y fórmula

La SFC publica el **ICV por vencimiento**, cuyo concepto es:

```text
ICV_t = saldo de cartera y leasing vencidos_t / saldo de cartera y leasing brutos_t × 100
```

El Excel histórico ya contiene el ratio publicado. El runner conserva el dato sin recalcularlo porque este snapshot no ofrece sus numerador y denominador como campos separados. El denominador conceptual es la cartera y leasing brutos del universo y modalidad publicados por la SFC; no es EAD de una operación. La metodología SFC define indicadores de vivienda separados por bandas de 1–4 meses y más de 4 meses; la serie histórica incluida presenta un ICV por modalidad, que aquí se conserva como reportado, sin reasignar alturas de mora.

No se suman bandas de mora: algunas alturas se traslapan en fuentes de detalle, y este archivo oficial ya publica el indicador agregado por vencimiento. Los valores vacíos se dejan ausentes; un cero numérico reportado se conserva como cero.

## Resultado reproducible

El snapshot tiene 156 meses, desde enero de 2011 hasta diciembre de 2023, y 21.050 observaciones numéricas válidas. En diciembre de 2023, la mediana no ponderada del ICV entre entidades fue: microcrédito 11,42% (n=21), consumo 7,31% (n=42), comercial 4,73% (n=41) y vivienda 2,20% (n=27). La mediana interinstitucional cambió en 12 meses +2,85, +2,41, +1,60 y +0,20 puntos porcentuales, respectivamente.

Son medianas de entidades con dato disponible, no tasas ponderadas del sistema. La composición varía por modalidad y a través del tiempo. No se infiere que los movimientos sean atribuibles al riesgo de las mismas entidades, exposiciones o cohortes.

- [Informe detallado, resultados y límites](results/official_proxy_report.md)
- [Distribución de ICV por modalidad](figures/sfc_icv_distribution_by_modality.png)
- [Serie entidad × modalidad × mes](results/sfc_icv_entity_modality_month.csv)
- [Distribuciones mensuales](results/sfc_icv_modality_distribution.csv)
- [Manifiesto y calidad](results/manifest.json)

## Fuente y linaje

Fuente primaria: [SFC — Calidad de cartera de establecimientos de crédito](https://www.superfinanciera.gov.co/publicaciones/10082252/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualcalidad-de-cartera-establecimientos-de-credito-10082252/). La metodología se conserva en [`sfc_metodologia_calidad_cartera.xls`](data/raw/sfc_metodologia_calidad_cartera.xls). Las hojas históricas indican periodicidad mensual y fuente en estados financieros. El snapshot bruto fue descargado del histórico oficial el 10 de noviembre de 2026 y su último corte observado es 2023-12; el archivo no es una alimentación actualizada en tiempo real.

SHA-256: `ee6bfe42fa1fff45716c2cc517c9099fbea15a1faac03d8f5109eed9aa5487be`.

SHA-256 de la metodología: `3d620d021637ab316f37ced98026665c0a9bbcdc10a2f17470508eeb560cd4bf`.

## Calidad y trade-offs

- Grano de la fuente: código de entidad × modalidad × mes. Se conservaron cuatro hojas de modalidad, 70 filas fuente por hoja y 156 encabezados mensuales comunes.
- Extracto: 21.050 ratios numéricos, 0 claves duplicadas, 0 ratios fuera de [0,1]. Celdas vacías omitidas: comercial 4.461; consumo 4.081; vivienda 6.765; microcrédito 7.323. La falta de dato no se imputa como cero.
- Se usan percentiles no ponderados entre entidades por mes, no agregación del sistema. Esto evita fabricar denominadores con información no incluida en el snapshot; a cambio, cada entidad tiene igual peso en la mediana y percentiles.
- Las diferencias de cobertura, entradas/salidas de entidades, fusiones, reclasificaciones y cambios de razón social pueden mover la distribución. Se incluye el código reportado como identificador; la equivalencia histórica requiere revisión.
- El corte de diciembre de 2023 limita vigencia. Para vigilancia actual hay que sustituir el snapshot con una edición contemporánea y conservar las versiones anteriores para trazabilidad.

## Límites de interpretación y validación necesaria

El ICV es un **stock agregado vencido / cartera bruta**, no tasa de entrada a default. La variación del ratio mezcla mora, curas, castigos, recaudos, amortizaciones, nuevas originaciones y composición. No valida PD de originación, scorecards, roll rates, probabilidades de transición, LGD, EAD, ECL IFRS 9, cosechas ni decisiones de crédito. El resultado puede orientar una alerta de segmento y stress exploratorio, no reemplaza datos de operación individual.

Para validar los modelos del laboratorio hacen falta snapshots por operación con fecha de observación, saldo bruto y vencido, edad de mora no traslapada, default aprobado, curas, castigos, originación, pagos y estado futuro, junto con criterios de inclusión y cobertura consistentes. Se requieren validación temporal y evaluación independiente antes de uso operacional.

## Reproducción

Desde esta carpeta:

```bash
python3 scripts/build_sfc_quality_proxy.py
```

Requiere Python con `openpyxl`, `pandas` y `matplotlib`. El runner usa el snapshot versionado y regenera CSV, manifiesto, figura e informe. No ejecuta ni modifica los laboratorios de datos controlados.
