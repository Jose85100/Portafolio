# Valoración DCF y múltiplos

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Separar valor de empresa y patrimonio; no confundir múltiplo de salida con análisis de comparables.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: estados financieros, forecast, tasa documentada, deuda neta, acciones y comparables fechados. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: FCFF = EBIT × (1-T) + depreciación - CAPEX - variación NWC; EV = PV(FCFF) + PV(valor terminal); equity = EV - deuda neta con ajustes documentados.

Salida: DCF por escenarios, sensibilidad WACC-g y comparables EV/EBITDA, EV/ventas o P/E según pertinencia. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Rango de negociación o selección de inversión con incertidumbre.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Comparables ajustados por crecimiento y rentabilidad frente a mediana simple; validar fuera de muestra y documentar selección.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
