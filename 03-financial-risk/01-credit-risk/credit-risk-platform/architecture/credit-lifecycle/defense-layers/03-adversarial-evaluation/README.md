# Evaluación adversarial y revisión de supuestos

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Buscar fallos de interacción, rutas alternativas y familias no vistas antes de liberar un cambio.

**Etapas:** Diseño, Calibración, Validación, Sombra.

**Responsable propuesto:** Validación/seguridad con alcance aprobado y separación respecto al autor; la entrega actual es autorrevisión documental.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Capacidad del actor | Definir qué controla y qué no: campo, sesión, documento ficticio, evento o rol de prueba. |
| Familias reservadas | Separar escenarios de desarrollo y test; incluir variaciones y casos legítimos cercanos. |
| Prueba de cadena | Evaluar evidencia, política, fallback, revisión y efecto; un control local fuerte puede quedar omitido en otra ruta. |

## Estudios adicionales de la capa

### ADV-CHAIN · Control fuerte seguido por fallback débil

**Diseño propuesto:** Combinar fuente inconclusa, recuperación de sesión y revisión con evidencia obsoleta; verificar invariantes terminales en el emulador futuro.

**Medición:** Avances indebidos, estado seguro, demora y cobertura de rutas.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### ADV-HOLDOUT · Familias no utilizadas para ajustar controles

**Diseño propuesto:** Reservar familias de escenarios sintéticos y evaluadores de referencia; fijar umbral antes del test y comparar genuinos por accesibilidad/dispositivo.

**Medición:** Éxito del escenario adversarial por familia, falsos bloqueos e incertidumbre; sin garantía universal.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [01-geo-device-context](../../projects/01-geo-device-context/README.md)
- [02-provider-orchestration](../../projects/02-provider-orchestration/README.md)
- [03-credit-offer-policy](../../projects/03-credit-offer-policy/README.md)
- [04-durable-origination-workflow](../../projects/04-durable-origination-workflow/README.md)
- [05-disbursement-reconciliation](../../projects/05-disbursement-reconciliation/README.md)
- [06-servicing-ledger-quality](../../projects/06-servicing-ledger-quality/README.md)
- [07-collections-treatment-design](../../projects/07-collections-treatment-design/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)
- [09-purpose-bound-signal-governance](../../projects/09-purpose-bound-signal-governance/README.md)
- [10-formalization-collateral](../../projects/10-formalization-collateral/README.md)

## Riesgo residual

- El corpus finito no prueba invulnerabilidad ni simula toda creatividad adversaria.
- Una revisión del autor no es un pentest, evaluación externa ni certificación.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
