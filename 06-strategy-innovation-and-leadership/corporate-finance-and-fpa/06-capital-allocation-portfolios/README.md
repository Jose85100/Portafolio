# Asignación de capital y portafolios

**Estado S1: especificación; no nueva implementación ejecutada.**

## Fundamentos y alcance

Separar cartera de proyectos empresariales de cartera de activos negociables.

## Arquitectura y motor propuesto

Fuentes versionadas → contratos y conciliación → supuestos/escenarios → cálculo → validación → memo de decisión.

Entradas: inversión inicial, flujos, dependencias, retornos, costos, liquidez y restricciones. Cada registro requiere moneda, unidad, fecha, origen, responsable y disponibilidad. Mantener periodos consistentes; datos faltantes no se convierten en cero.

Base de cálculo: Maximizar suma de VPN_i × x_i bajo presupuesto y dependencias; para activos, optimizar riesgo-retorno neto de costos con validación temporal.

Salida: Frontera presupuesto-valor, selección de proyectos y sensibilidad; enlace con asset management. Reportar caso base, escenario adverso, sensibilidad y límites. Evitar recomendaciones sin identificar condiciones y supuestos.

## Decisión que apoya

Qué proyectos financiar, cuánto asignar y qué inversiones posponer.

## Responsabilidad y evidencia

En un caso real, completar [ficha de responsabilidad](../CASE_TEMPLATE.md): qué hizo el usuario, qué elaboró el equipo, quién aprobó y qué decisión se tomó. No atribuir autoría o responsabilidad basándose únicamente en que un artefacto esté en el repositorio.

## Investigación y validación

Optimización robusta frente a ranking por TIR; comparar valor y violaciones bajo escenarios reservados.

Antes de promover el motor a prototipo: caso manual, pruebas de signos y unidades, reconciliación de caja/balance, notebook con fórmulas y gráficos, datos autorizados y comparación con baseline. No se han ejecutado experimentos nuevos en esta carpeta.
