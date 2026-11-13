# Flujo de caja y tesorería

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Construir flujo directo de 13 semanas y mensual de largo plazo; diferenciar caja, EBITDA y utilidad.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: saldos bancarios conciliados, cuentas por cobrar/pagar, nómina, impuestos y compromisos. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: Caja final = caja inicial + cobros - pagos + desembolsos - servicio de deuda; necesidad = max(0, caja mínima - caja prefondeo).

Salida: Calendario de cobros/pagos, alertas de déficit y escenarios de recaudo. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Orden de pagos, reserva de caja y fecha de contratación de fondeo.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Cobros con retrasos correlacionados frente a DSO fijo; validar error de saldo mínimo y anticipación de déficit.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
