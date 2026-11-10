# BCP, ciberseguridad y terceros

**Estado S1: diseño.** Servicios críticos, recuperación y concentración tecnológica.

## Fundamentos

Brecha de recuperación = tiempo observado - objetivo; RTO y RPO distintos. Las expresiones son bases de investigación, no sustitutos de anexos regulatorios. Consultar [fuentes y perímetro](../SOURCES.md).

## Datos y contratos

Campos mínimos: servicio, dependencia, proveedor, incidente, objetivo de recuperación. Declarar grano, moneda, unidades, corte, fecha efectiva, fecha de disponibilidad, licencia, origen y versión. Rechazar duplicados de clave; no imputar cero a datos desconocidos. Separar datos sintéticos de observaciones reales.

## Arquitectura y motor propuesto

Adaptador de fuentes → validación de contratos → selección de reglas por entidad y fecha → motor específico → conciliación → evidencia y revisión humana. Ver [arquitectura transversal](../00-architecture/README.md).

Reutilizar [componentes existentes](../../05-enterprise-risk-advisory/04-cyber-ai/) antes de crear implementaciones paralelas. El motor propuesto debe exponer entradas tipadas, parámetros, resultados desagregados y razones de excepciones.

## Tres líneas de investigación

1. Grafos de dependencias: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
2. pruebas de salida de proveedor: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
3. ejercicios de recuperación: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.

## Validación y aceptación

- Casos manuales y conciliación de totales; sensibilidad y límites de parámetros.
- Datos point-in-time y separación temporal cuando haya estimación.
- Pruebas de entradas inválidas, unidades incompatibles, faltantes y perímetro.
- Comparar resultados con fuente/anexo oficial aplicable antes de afirmar cumplimiento.
- Entregar notebook con fórmulas, gráficos de sensibilidad, resultados calculados y límites; Python como referencia y C++ solo si un benchmark justifica migración.

**Responsables objetivo:** dueño de riesgo define políticas; datos mantiene contratos; ingeniería implementa; validación independiente cuestiona métodos; cumplimiento verifica aplicabilidad; comité decide excepciones. Ninguna alerta constituye una decisión automática de cumplimiento.
