# Inflación de materiales y suministro

**Laboratorio:** diseño metodológico en desarrollo; no calibrado ni validado para estimar sobrecostos de obras. **Edición complementaria con datos observados:** análisis descriptivo reproducible de ICOCED del DANE para tres insumos en Bogotá y Cundinamarca.

## Decisión que habilita

Un promotor, constructor o financiador puede usar señales públicas de variación de costos para identificar partidas que merecen revisión de escaladores, cláusulas de reajuste, calendario de compra o contingencias presupuestales. Esta edición encuentra diferencias de trayectoria entre acero corrugado, cemento y concreto común; orienta una revisión de exposición y no cuantifica por sí sola el costo de una obra.

## Aplicación observada

Se toma la serie mensual publicada por el DANE en **ICOCED, Anexo 7.2**, para el dominio geográfico `Bogotá_Cundinamarca AR`, grupo de costos `Materiales`, de enero de 2022 a septiembre de 2026. Se extraen tres índices de insumo, sus variaciones mensuales y ponderaciones de la base de 2021.

| Insumo | Peso de referencia 2021 (%) | Índice ene-2022 | Índice sep-2026 | Cambio del índice en la ventana (%) | Desv. estándar mensual (pp) | P95 de cambio mensual (%) |
|---|---:|---:|---:|---:|---:|---:|
| Acero corrugado | 7.878 | 99.405 | 95.120 | -4.31 | 2.310 | 3.654 |
| Cemento | 7.357 | 103.510 | 131.270 | 26.82 | 2.202 | 5.456 |
| Concreto común | 10.112 | 100.733 | 133.070 | 32.10 | 2.346 | 2.578 |

El índice de concreto común aumentó 32.10% entre enero de 2022 y septiembre de 2026, mientras que el índice de acero corrugado terminó 4.31% por debajo de enero de 2022. Son movimientos de índices durante esta ventana; no son precios pagados, pronósticos ni impactos monetarios sobre presupuestos.

## Figuras y reporte

- [Informe reproducible](results/official_report.md)
- [Trayectorias del índice](figures/icoced_indices.png)
- [Volatilidad histórica móvil](figures/icoced_volatility.png)
- [Serie procesada](results/icoced_material_series_bogota.csv)
- [Manifiesto de fuente, hash y calidad](results/manifest.json)

## Fuente, linaje y calidad

Fuente primaria: [DANE, ICOCED históricos](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-costos-de-la-construccion-de-edificaciones-icoced/indice-de-costos-de-la-construccion-de-edificaciones-icoced-historicos). El snapshot utilizado es [el anexo de septiembre de 2026](data/raw/dane_icoced_sep2026.xlsx), con URL directa publicada por el DANE: [anex-ICOCED-sep2026.xlsx](https://www.dane.gov.co/files/operaciones/ICOCED/anex-ICOCED-sep2026.xlsx). El libro declara actualización el 30 de septiembre de 2026.

- Hoja: `Anexo 7.2`; fuente en base diciembre de 2021 = 100.
- Grano extraído: insumo × dominio geográfico × mes; 57 meses por insumo y 171 observaciones.
- Calidad comprobada: 3 filas fuente esperadas y observadas; 171 valores mensuales esperados y observados; 0 claves duplicadas; 0 valores mensuales ausentes o no numéricos en la selección; no se imputaron ni agregaron filas.
- SHA-256 del snapshot: `c858c33819bbc2fc6db3e80aa971be07991e06aa2914330f7ae0da95e4d1b63b`.
- El DANE explica que ICOCED es el rediseño de ICCV desarrollado en 2021. El índice mide variaciones de costos de una canasta representativa; no es un índice de precios transaccionales ni mide el costo total de construcción.

## Registro de decisiones

| Decisión | Motivo y trade-off |
|---|---|
| Usar tres series de insumos publicadas por DANE, en vez de calcular un índice propio de materiales | Evita sustituir las ponderaciones y fórmulas oficiales por una agregación no documentada. Se pierde una medida única de “materiales”; se conserva la señal por insumo. |
| Limitar el resultado a Bogotá y Cundinamarca | Mantiene una única cobertura geográfica compatible con el uso local. No representa el resto del país ni la ubicación concreta de cada obra. |
| Reportar desviación estándar y percentil 95 históricos | Resume dispersión y shocks observados; no asume una distribución ni convierte el percentil en probabilidad futura. |
| Mantener la edición como anexo al laboratorio | Los datos oficiales validan que hay señales de costos observables; no validan la ecuación de pérdida del proyecto, los lead times ni la eficacia de mitigaciones. |

## Gobierno, limitaciones y validación pendiente

El DANE documenta que [ICOCED es el rediseño del ICCV desarrollado durante 2021](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-costos-de-la-construccion-de-edificaciones-icoced/indice-de-costos-de-la-construccion-de-edificaciones-icoced-historicos). El [boletín técnico de ICOCED](https://www.dane.gov.co/files/operaciones/ICOCED/bol-ICOCED-feb2025.pdf) describe la medición de variaciones de costos. El índice utiliza diciembre de 2021 como base; sus pesos de insumo no necesariamente describen la mezcla, el contrato, las cantidades, el proveedor o la fecha de compra de una obra determinada. La variación del índice no estima un retorno de caja, inflación contractual, costo de reposición ni pérdida del deudor.

Para validar su aplicación a una empresa o proyecto se requieren presupuesto desagregado y versiones, cantidades, ubicación, fechas y órdenes de compra, contratos y cláusulas de ajuste, cotizaciones y facturas, proveedores, cronograma y fechas de entrega. El análisis debe alinear partidas con insumos y períodos, comparar el índice con precios efectivamente pagados, medir errores fuera de muestra y someter los escenarios de costo a revisión independiente. Sin estos datos no se estima `DeltaCost = sum_i Quantity_i × DeltaPrice_i`, retrasos de suministro, sustitución de insumos ni efecto financiero.

La serie termina en septiembre de 2026 según el snapshot, no es un dato en tiempo real y puede tener posteriores publicaciones. No se hacen inferencias causales ni extrapolaciones. Los resúmenes describen solo las observaciones públicas seleccionadas y no son un modelo de pronóstico.

## Reproducción

Desde esta carpeta, ejecutar:

```bash
python3 scripts/run_official_application.py
```

Requiere Python con `openpyxl`, `pandas` y `matplotlib`. El runner usa únicamente el snapshot versionado y regenera manifiesto SHA-256, CSV, resumen, figuras e informe en `results/` y `figures/`.

## Especificación del laboratorio

La hipótesis de trabajo sigue siendo `DeltaCost = sum_i Quantity_i × DeltaPrice_i`, complementada con exposición a retrasos y sustitución. La validación de esa hipótesis requiere datos internos; la edición observada de ICOCED no los reemplaza. El trabajo metodológico pendiente incluye contrato de datos, target sin leakage, benchmark, validación temporal, sensibilidad y revisión independiente antes de cualquier uso operativo.
