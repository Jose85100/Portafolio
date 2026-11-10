# SARO y riesgo operacional

**Estado S1: diseño.** Eventos, causas, controles y pérdidas.

## Fundamentos

L_anual = suma de severidades; frecuencia y severidad separadas. Las expresiones son bases de investigación, no sustitutos de anexos regulatorios. Consultar [fuentes y perímetro](../SOURCES.md).

## Datos y contratos

Campos mínimos: evento, fecha ocurrencia, fecha registro, pérdida bruta, recuperación, proceso. Declarar grano, moneda, unidades, corte, fecha efectiva, fecha de disponibilidad, licencia, origen y versión. Rechazar duplicados de clave; no imputar cero a datos desconocidos. Separar datos sintéticos de observaciones reales.

## Arquitectura y motor propuesto

Adaptador de fuentes → validación de contratos → selección de reglas por entidad y fecha → motor específico → conciliación → evidencia y revisión humana. Ver [arquitectura transversal](../00-architecture/README.md).

Reutilizar [componentes existentes](../../05-enterprise-risk-advisory/03-operational-resilience/) antes de crear implementaciones paralelas. El motor propuesto debe exponer entradas tipadas, parámetros, resultados desagregados y razones de excepciones.

## Tres líneas de investigación

1. Subregistro de eventos: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
2. dependencia entre fallas: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
3. eficacia de controles con incertidumbre: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.

## Validación y aceptación

- Casos manuales y conciliación de totales; sensibilidad y límites de parámetros.
- Datos point-in-time y separación temporal cuando haya estimación.
- Pruebas de entradas inválidas, unidades incompatibles, faltantes y perímetro.
- Comparar resultados con fuente/anexo oficial aplicable antes de afirmar cumplimiento.
- Entregar notebook con fórmulas, gráficos de sensibilidad, resultados calculados y límites; Python como referencia y C++ solo si un benchmark justifica migración.

**Responsables objetivo:** dueño de riesgo define políticas; datos mantiene contratos; ingeniería implementa; validación independiente cuestiona métodos; cumplimiento verifica aplicabilidad; comité decide excepciones. Ninguna alerta constituye una decisión automática de cumplimiento.
