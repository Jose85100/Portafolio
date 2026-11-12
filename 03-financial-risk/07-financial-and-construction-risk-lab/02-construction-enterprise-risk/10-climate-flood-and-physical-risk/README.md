# Riesgo climático físico

**Estado:** diseño con companion de contexto de emergencias reportadas UNGRD 2025. **No calibrado ni validado.**

## Pregunta y alcance
Amenazas por ubicación y vulnerabilidad del activo. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
EAL = sum_s P(s)*Damage(s)
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Incertidumbre espacial y riesgo de cola. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Evidencia pública disponible

La [companion UNGRD 2025](UNGRD_2025_COMPANION.md) agrega filas del registro de inundaciones, crecientes súbitas, avenidas torrenciales y movimientos en masa por departamento/municipio. Solo 2 de 6.506 filas tienen coordenada distinta de cero; el campo etiquetado DIVIPOLA es inconsistente entre filas. Por ello este insumo permite inspeccionar cobertura de reportes, pero no validar localización, frecuencia de amenaza, exposición física o pérdidas de un proyecto. Se evita sumar impactos de filas que pueden representar actualizaciones repetidas.
