# Controles humanos, recuperación e intervención interna

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Impedir que presión, urgencia, ingeniería social o privilegio interno sustituyan evidencia y atribución.

**Etapas:** Soporte, Recuperación de cuenta, Analista/comité, Cambios de cuenta o términos.

**Responsable propuesto:** Operaciones y seguridad; segregación de funciones según criticidad y política institucional.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Atribución verificable | Roles, finalidad de tarea, razones y evidencia para cada override; mínimo privilegio y trazabilidad. |
| Recuperación evaluada | Cambiar teléfono/autenticador/destino reabre los controles que realmente pierden validez. |
| Excepciones gobernadas | Ruta de emergencia explícita y revisada; no un permiso universal de bypass ni una aprobación por urgencia. |

## Estudios adicionales de la capa

### HUMAN-OVERRIDE · Solicitud urgente sin atribución suficiente

**Diseño propuesto:** Guiones ficticios de revisión de escritorio y roles de prueba; alternar rol, evidencia y vigencia sin contactar personas reales.

**Medición:** Overrides inválidos, tiempo de resolución y rechazo de excepciones legítimas.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### HUMAN-RECOVERY · Cambio de contacto después de verificar identidad

**Diseño propuesto:** Evento sintético de cambio de número o cuenta con revisión/OTP favorable anterior; comprobar nueva vinculación y tratamiento de la evidencia previa.

**Medición:** Precondiciones obsoletas aceptadas, trazabilidad y carga de nueva evidencia.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [04-durable-origination-workflow](../../projects/04-durable-origination-workflow/README.md)
- [05-disbursement-reconciliation](../../projects/05-disbursement-reconciliation/README.md)
- [07-collections-treatment-design](../../projects/07-collections-treatment-design/README.md)
- [10-formalization-collateral](../../projects/10-formalization-collateral/README.md)

## Riesgo residual

- Dos revisores que comparten la misma premisa equivocada no garantizan independencia.
- La colusión interna exige controles de acceso y auditoría además del score de cliente.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
