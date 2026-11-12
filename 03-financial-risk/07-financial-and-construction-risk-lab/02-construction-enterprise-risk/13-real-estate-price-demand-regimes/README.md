# Regímenes de precios y absorción

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Aplicación observada: cambio de precios del IPVN

El companion [observed-dane-ipvn-price-regimes](observed-dane-ipvn-price-regimes/README.md) compara la variación trimestral nacional del IPVN publicada por DANE (2004-I–2026-II). Es una referencia sectorial de precios; no observa absorción ni resultados de obra, y no valida el modelo de regímenes propuesto abajo. La fuente, el hash, la reproducción, la lectura del último trimestre y las limitaciones están documentadas en su ficha.

## Pregunta y alcance
Markov switching para precios, inventario y velocidad de ventas. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
P(S_t=j|S_{t-1}=i) = p_ij
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Cambio estructural, pronósticos por régimen. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.
