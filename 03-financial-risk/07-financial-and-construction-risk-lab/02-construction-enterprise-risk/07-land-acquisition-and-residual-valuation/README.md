# Riesgo de adquisición de suelo

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Pregunta y alcance
Valor residual de lote y sensibilidad a aprovechamiento. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
LandResidual = PV(Revenue)-PV(Costs)-RequiredMargin
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Riesgo normativo, licencias y sensibilidad de precios. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Contexto observado DANE: variación de avalúos residenciales

Se añadió el companion [DANE IVP residencial 2024–2025](observed-dane-ivp-residential-valuation/README.md), con resultados oficiales para 22 ciudades. Aporta una referencia contextual para supuestos de valor de salida/collateral: la variación IVP 2025 osciló entre 2,23% (Quibdó) y 6,48% (Manizales), frente al 3,45% nacional publicado por DANE.

Esta evidencia **no cierra la validación del residual de suelo**: el IVP mide valoración de predios urbanos habitacionales, excluye Bogotá y no es un índice de lotes, oferta, transacciones ni absorción. El proyecto sigue requiriendo comparables de suelo por microzona y resultados autorizados de adquisición/venta enlazados con costos, norma y edificabilidad.
