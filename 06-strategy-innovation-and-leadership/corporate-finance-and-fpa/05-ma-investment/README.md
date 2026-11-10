# M&A y evaluación de inversiones

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Distinguir valoración stand-alone, sinergias, precio pagado y costos de integración.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: flujos separados, precio, deuda asumida, sinergias, impuestos, integración y financiación. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: VPN comprador = valor stand-alone + PV(sinergias netas no incluidas) - contraprestación; usar bases de valor consistentes.

Salida: Puente de valor, escenarios de captura, fuentes/usos y plan de integración. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Comprar, esperar, negociar precio o rechazar; identificar condiciones que cambian la decisión.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Sinergias con retrasos y costos correlacionados frente a porcentaje fijo; falsar si no mejora diagnóstico de escenarios adversos.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
