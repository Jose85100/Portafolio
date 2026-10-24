# Respuesta, contención y aprendizaje de incidentes

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Limitar impacto, preservar evidencia y corregir controles sin reescribir efectos ni convertir sospechas en labels confirmadas.

**Etapas:** Detección, Operaciones, Pagos, Aprendizaje posterior.

**Responsable propuesto:** Gestión de incidentes con fraude, seguridad, pagos, atención y jurídica según el caso.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Contención proporcional | Definir estado pendiente/revisión/ruta degradada y responsables; distinguir señal, sospecha y caso adjudicado. |
| Preservación y conciliación | Conservar referencias/versiones y efectos; proteger acceso a evidencia y registrar correcciones. |
| Retorno controlado | Corrección, replay, comparación con genuinos y liberación aprobada; actualizar taxonomía y estudios. |

## Estudios adicionales de la capa

### RESP-TIMEOUT · Incidente con pago ya liquidado

**Diseño propuesto:** Simulación de alerta tardía más pago confirmado; comprobar que la contención no borra un efecto ni libera exposición ficticiamente.

**Medición:** Pérdida de trazabilidad, dobles efectos, pendientes por edad y tiempo de resolución.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### RESP-LABEL · Aprendizaje tras incidente sin envenenar labels

**Diseño propuesto:** Corpus distingue sospechas, casos descartados y adjudicados; comparar reentrenamiento ingenuo con taxonomía/maduración y evaluación congelada.

**Medición:** Etiquetas incorrectas incorporadas, falso positivo posterior y calidad de trazabilidad.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [04-durable-origination-workflow](../../projects/04-durable-origination-workflow/README.md)
- [05-disbursement-reconciliation](../../projects/05-disbursement-reconciliation/README.md)
- [07-collections-treatment-design](../../projects/07-collections-treatment-design/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)

## Riesgo residual

- La respuesta técnica no garantiza recuperación de dinero ni revierte por sí sola un pago.
- La conservación de evidencia debe conciliarse con acceso, finalidad y obligaciones aplicables.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
