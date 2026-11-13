# Calidad y garantías

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Señal observada de sanciones

El [companion SIC de sanciones firmes en Inmuebles](observed-sic-real-estate-sanctions/README.md) analiza un dataset oficial por resolución, fecha y conducta, sin conservar nombres ni identificadores de caso. En el corte del 11 de noviembre de 2026 hay 142 filas que corresponden a 126 resoluciones únicas de 2013 a 2026; 16 resoluciones contienen al menos una conducta cuyo rótulo incluye “Calidad”. Es una señal de enforcement de protección al consumidor, no una frecuencia de defectos ni de reclamos bajo garantía. El diseño de reservas sigue sin calibración o validación institucional.

## Evidencia pública y brecha

La [SIC informó](https://sedeelectronica.sic.gov.co/comunicado/comunicado-de-interes-sobre-la-proteccion-de-los-derechos-de-las-y-los-consumidores-en-proyectos-de-vivienda-nueva) que recibió 2.818 denuncias y 3.255 demandas relacionadas con presuntas vulneraciones a consumidores de vivienda nueva entre enero de 2024 y octubre de 2025. La comunicación incluye fallas de garantía entre varios motivos, junto con retrasos y otros incumplimientos; no desglosa el total en reclamaciones por defectos, proyecto, costo, reparación o pago. Es contexto de demanda de protección al consumidor, no una frecuencia de siniestros ni base actuarial para reservas. Los requisitos y límites están detallados en [DATA_GAP.md](DATA_GAP.md).

## Pregunta y alcance
Reservas por defectos post-entrega y siniestralidad. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
Reserve = E[ClaimCount*ClaimSeverity]
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Triángulos de desarrollo, IBNR y maduración. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.
