# Presupuesto y proyecciones

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Definir ingresos por volumen y precio, OPEX por responsable, CAPEX, impuestos y capital de trabajo; conectar resultados, balance y caja.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: ventas, precios, clientes, plantilla, proveedores, CAPEX, cobros y pagos por mes. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: Ingresos = volumen × precio; variación = real - presupuesto; separar efectos volumen, precio, mezcla y calendario.

Salida: Modelo mensual 36 meses, forecast móvil y puente presupuesto-real. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Qué gastos y contrataciones financiar, cuándo crecer y cuánto capital se necesita.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Drivers y forecast probabilístico frente a presupuesto fijo; backtesting temporal y cobertura de intervalos.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
