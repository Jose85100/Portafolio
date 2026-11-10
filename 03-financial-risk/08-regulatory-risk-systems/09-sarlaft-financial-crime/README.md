# SARLAFT y delitos financieros

**Estado S1: diseño.** Debida diligencia, alertas y análisis humano.

## Fundamentos

Tasa de alertas útiles = casos confirmados / alertas revisadas; etiquetas incompletas. Las expresiones son bases de investigación, no sustitutos de anexos regulatorios. Consultar [fuentes y perímetro](../SOURCES.md).

## Datos y contratos

Campos mínimos: cliente, beneficiario final, transacción, jurisdicción, señal, decisión. Declarar grano, moneda, unidades, corte, fecha efectiva, fecha de disponibilidad, licencia, origen y versión. Rechazar duplicados de clave; no imputar cero a datos desconocidos. Separar datos sintéticos de observaciones reales.

## Arquitectura y motor propuesto

Adaptador de fuentes → validación de contratos → selección de reglas por entidad y fecha → motor específico → conciliación → evidencia y revisión humana. Ver [arquitectura transversal](../00-architecture/README.md).

Reutilizar [componentes existentes](../../05-enterprise-risk-advisory/05-financial-crime/) antes de crear implementaciones paralelas. El motor propuesto debe exponer entradas tipadas, parámetros, resultados desagregados y razones de excepciones.

## Tres líneas de investigación

1. Grafos temporales: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
2. priorización con capacidad limitada: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
3. drift y sesgo de investigación: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.

## Validación y aceptación

- Casos manuales y conciliación de totales; sensibilidad y límites de parámetros.
- Datos point-in-time y separación temporal cuando haya estimación.
- Pruebas de entradas inválidas, unidades incompatibles, faltantes y perímetro.
- Comparar resultados con fuente/anexo oficial aplicable antes de afirmar cumplimiento.
- Entregar notebook con fórmulas, gráficos de sensibilidad, resultados calculados y límites; Python como referencia y C++ solo si un benchmark justifica migración.

**Responsables objetivo:** dueño de riesgo define políticas; datos mantiene contratos; ingeniería implementa; validación independiente cuestiona métodos; cumplimiento verifica aplicabilidad; comité decide excepciones. Ninguna alerta constituye una decisión automática de cumplimiento.

## SARLAFT y SAGRILAFT: separación de regímenes

El nombre es **SARLAFT**. La fuente SFC se registra en [cumplimiento LA/FT/FPADM](https://www.superfinanciera.gov.co/publicaciones/10116062/cumplimiento-tecnico-laftfpadm/). [SAGRILAFT](../13-sagrilaft/) tiene carpeta propia y fuentes Supersociedades. Compartir componentes de identidad, beneficiarios finales, segmentación y casos no permite intercambiar sujetos obligados, requisitos ni reportes.

### Motores específicos propuestos

- Segmentación point-in-time con variables permitidas, explicación y estabilidad temporal.
- Resolución de entidades y grafos de beneficiarios finales, con procedencia de cada enlace.
- Monitoreo por escenarios y priorización de casos según capacidad de revisión.
- Gestor de diligencias, decisiones, evidencias y vencimientos.

Son diseños. No se ha implementado envío de ROS ni conexión UIAF; toda decisión y reporte requiere proceso autorizado y revisión humana. La calidad del modelo debe medirse con etiquetas incompletas, falsos positivos y costo operativo, evitando interpretar alerta como prueba de delito.
