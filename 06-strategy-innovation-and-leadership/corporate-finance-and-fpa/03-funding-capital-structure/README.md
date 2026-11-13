# Fondeo y estructura de capital

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Comparar deuda, equity, aportes de socios y financiación por etapas con restricciones de caja.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: tasas, comisiones, amortización, garantías, covenants, dilución y desembolsos. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: DSCR = CFADS / servicio de deuda cuando el denominador es positivo; modelar interés sobre saldo y comisiones por separado.

Salida: Cronogramas de deuda, costo efectivo, dilución y holgura de covenants. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Monto, instrumento, plazo y oportunidad del fondeo.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Financiación contingente a hitos frente a ronda única; contrastar costo, dilución y frecuencia de déficit.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
