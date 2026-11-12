# Capital de trabajo y liquidez

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Evidencia oficial observada

El companion [Supersociedades: cobertura de insumos y rotación de inventarios](observed-supersociedades-working-capital-coverage/README.md) enlaza la cohorte oficial de 1.000 empresas (reporte 2025, corte 2024) con estados NIIF de 2023 y 2024, alineando NIT y base de presentación en memoria. No guarda filas individuales ni identificadores. Publica cobertura por macrosector y una métrica DIO de casos completos; no construye DSO, DPO, ciclo de conversión de efectivo ni forecast porque las ventas a crédito y las compras a proveedores no están separadas en los conceptos públicos usados.

Para el corte 2024 hubo 642/1.000 reportes alineados; en 2023, 615/1.000. El set de los tres rubros de balance estuvo completo para 554 empresas en 2023 y 581 en 2024. Ingresos y costo de ventas estuvieron presentes simultáneamente para 626. El componente DIO pudo calcularse para **543 entidades (54,3%)**. Su cobertura por macrosector va de **18,3% en servicios a 70,9% en comercio**; la mediana DIO va de 11,18 días en servicios a 85,75 días en construcción. Las diferencias describen esta muestra grande seleccionada por ingresos, no el universo empresarial ni riesgo de caja.

La brecha semántica y el contrato mínimo para DSO/DPO/CCC se detallan en [DATA_GAP.md](DATA_GAP.md). El modelo de forecast continúa en diseño y no está calibrado ni validado.

## Pregunta y alcance
Modelo de DSO/DPO/DIO y caja por vencimientos. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
CashConversionCycle = DSO + DIO - DPO
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
MAE y cobertura de intervalos en rolling forecast. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.
