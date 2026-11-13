# SREP y revisión supervisora comparada

**Estado S1: especificación.** SREP se estudia en su contexto europeo; no se presenta como obligación automática de una entidad colombiana.

## Fundamentos y fuentes

Revisión de modelo de negocio, gobierno y riesgos para capital y liquidez. Relacionar evidencia ICAAP/ILAAP, hallazgos y acciones sin inventar calificaciones supervisoras.

[EBA: revisión SREP publicada en junio de 2026](https://www.eba.europa.eu/publications-and-media/press-releases/eba-reaches-another-important-milestone-enhancing-supervisory-efficiency-its-revised-srep-guidelines): la fuente indica aplicación desde 2027-01-01. Conservar reglas y evidencia por fecha; verificar la versión aplicable al periodo de estudio.
[EBA: información ICAAP/ILAAP](https://www.eba.europa.eu/guidelines-icaap-and-ilaap-information).

## Arquitectura y motores propuestos

Repositorio de evidencias → taxonomía de riesgos → evaluación por dimensión → hallazgos revisados → acciones y seguimiento.

- Motor de completitud: requisito, fuente, documento, propietario, vigencia y revisión.
- Motor de hallazgos: criticidad definida por política, dependencias y plazos; no produce rating supervisor oficial.
- Motor de consistencia: contrastar escenarios de negocio, capital y liquidez usados en ICAAP/ILAAP.

## Tres ideas verificables

1. Detectar contradicciones entre planes de capital y liquidez con restricciones contables.
2. Priorizar cierre de hallazgos por dependencia y costo, comparando con orden por antigüedad.
3. Evaluar pérdida de cobertura causada por documentos desactualizados con casos de verdad conocida.

Validar con expedientes simulados, revisión manual y trazabilidad requisito-evidencia. Reutilizar [capital e ICAAP/ILAAP](../08-capital-rwa-icaap-ilaap/); no duplicar cálculos.
