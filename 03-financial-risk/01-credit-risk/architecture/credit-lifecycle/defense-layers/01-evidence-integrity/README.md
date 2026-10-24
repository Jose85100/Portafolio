# Integridad, procedencia y vínculo de evidencia

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Evitar que un archivo, teléfono, rostro o respuesta de proveedor favorable se use para afirmar algo que no verificó.

**Etapas:** Captación, KYC, Formalización, Antes del desembolso.

**Responsable propuesto:** Identidad/seguridad de canal y operaciones; el proveedor especializado aporta una verificación acotada.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Separación de hechos | Identidad reclamada, control del número, titularidad nominal, documento, vínculo con persona e intención conservan estados distintos. |
| Binding | Caso/sujeto/sesión/versión/vigencia enlazados; el resultado de otro expediente no satisface la precondición. |
| Autenticidad y soporte | OCR, hash, comparación facial y autenticidad de fuente tienen alcances diferentes; conservar inconcluso y ruta alternativa. |

## Estudios adicionales de la capa

### PHONE-LINK · Teléfono controlado con identidad reclamada distinta

**Diseño propuesto:** Proveedor simulado confirma posesión/OTP pero deja identidad vinculada sin corroborar. Contrastar con un titular legítimo que usa una línea compartida. La política no promociona el primer pase a identidad ni rechaza automáticamente el segundo caso.

**Medición:** Usos indebidos del pase de teléfono, carga de revisión y falsos bloqueos.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### DOCUMENT-LINK · Documento modificado o reutilizado con OCR correcto

**Diseño propuesto:** Archivos totalmente ficticios marcados NO VÁLIDO: campos coherentes con origen no corroborado y evidencia de sujeto diferente. Separar lectura, autenticidad, vínculo y condiciones de efecto.

**Medición:** Afirmaciones sin soporte, casos que avanzan sin evidencia y abstenciones justificadas.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [02-provider-orchestration](../../projects/02-provider-orchestration/README.md)
- [04-durable-origination-workflow](../../projects/04-durable-origination-workflow/README.md)
- [10-formalization-collateral](../../projects/10-formalization-collateral/README.md)
- [05-disbursement-reconciliation](../../projects/05-disbursement-reconciliation/README.md)

## Riesgo residual

- Un actor puede controlar una línea y aportar una identidad aparente consistente; OTP por sí solo no resuelve el vínculo.
- La integridad de bytes no acredita un emisor real; fuentes comprometidas o sin cobertura mantienen riesgo residual.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
