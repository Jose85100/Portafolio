# Vigilancia continua y detección de degradación

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Detectar pérdida de cobertura, cambios de proveedor y controles omitidos mientras se conserva diagnóstico y rollback.

**Etapas:** Producción futura, Monitoreo, Release, Validación.

**Responsable propuesto:** MLOps/datos, fraude y model risk; diagnóstico previo a cualquier liberación.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Métricas de sistema | Registrar control ejecutado, fuente disponible, transición y resultado; no solo AUC o tasa de aprobación. |
| Canarios de prueba internos | Fixtures sintéticos identificados y aislados del entrenamiento/estadísticas de clientes para comprobar rutas. |
| Cambio gobernado | Versión desconocida o deriva abre investigación; no implica automáticamente reentrenar o relajar controles. |

## Estudios adicionales de la capa

### ASSURE-CANARY · Control omitido pese a servicio saludable

**Diseño propuesto:** Un emulador devuelve 200 y esquema válido pero omite una comprobación; canarios internos etiquetados verifican la ruta sin mezclarse con clientes.

**Medición:** Omisiones detectadas, demora y contaminación de estadísticas por pruebas.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### ASSURE-HORIZON · Alarmas repetidas y cambio de cobertura

**Diseño propuesto:** Series sintéticas con múltiples canales, retraso de labels y referencias cambiantes; evaluar carga y error por horizonte.

**Medición:** Falsas alarmas conjuntas, demora de detección, cobertura y madurez.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [02-provider-orchestration](../../projects/02-provider-orchestration/README.md)
- [06-servicing-ledger-quality](../../projects/06-servicing-ledger-quality/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)
- [09-purpose-bound-signal-governance](../../projects/09-purpose-bound-signal-governance/README.md)

## Riesgo residual

- Un canario conocido no sustituye familias de evaluación no vistas.
- Ausencia de alarma no prueba seguridad; los labels pueden madurar tarde.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
