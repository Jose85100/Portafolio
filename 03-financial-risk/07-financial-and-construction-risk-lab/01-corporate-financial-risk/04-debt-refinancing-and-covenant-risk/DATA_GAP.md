# Brecha de datos: refinanciación y covenants

**Corte de revisión:** 2026-11-11. **Estado:** no existe deuda por emisor ni historia enlazada de covenants, DSCR y breach.

El companion de [tasa comercial BanRep](../03-credit-spread-and-refinancing-risk/observed-banrep-commercial-credit-cost/README.md) aporta contexto de tasas agregadas de nuevos préstamos. La [sensibilidad DSCR](observed-banrep-dscr-sensitivity/README.md) traduce esa historia a cobertura de interés para deuda y CFADS hipotéticos. Ninguna fuente identifica la tasa pactada, spread, vencimiento, covenants, calendario de amortización, breach/cure ni probabilidad de renovación de una empresa. Tampoco la sensibilidad DTF de la ruta de project finance valida un contrato corporativo.

## Datos mínimos

1. Instrumento/deuda seudonimizado, saldo y cronograma por corte, moneda, índice, margen, fees, amortización, vencimiento y garantías.
2. Covenants firmados, umbrales y modificaciones, cálculos fechados, dispensas, breach/cure y aprobación de acreedores.
3. EBITDA/CFADS y caja conciliados, plan y resultados, ofertas/cotizaciones de refinanciación y tasa finalmente contratada.
4. Ventana histórica de vencimientos, outcomes de rollover/default y costos de emisión para validar severidad.

La aceptación exige reconstrucción independiente de los cálculos contractuales, análisis de cohortes por fecha de vencimiento, escenarios de tasas/spread, backtesting fuera de tiempo y criterios aprobados antes de calibrar. El companion público actual no cumple estos requisitos de emisor.
