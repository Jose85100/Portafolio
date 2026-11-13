# Revisión de prior art y diferenciación

La propuesta se compara con tres candidatas de trabajo para este ciclo.

| Candidata | Brecha y precedentes | Viabilidad actual | Decisión |
|---|---|---|---|
| A. Integridad/completitud de un bundle local de evidencia | El ledger existente menciona hashes y DAG, pero sólo como propuesta; MLflow registra parámetros, código, métricas y artefactos; W3C PROV modela entidades, actividades y agentes. Falta una demostración ejecutable en este árbol que pruebe corrupciones y abstención por evidencia incompleta. | Alta: fixtures pequeños, oracle estructural y sin datos privados. | Elegida; completa un vacío de implementación con un caso falsable. No reclama novedad criptográfica. |
| B. Provenance firmada del builder y verificación contra root-of-trust | SLSA e in-toto ya especifican attestations, firmas, identidades de builder y verificación contra expectativas. TUF aborda roles, umbrales, expiración y anti-rollback. Una implementación correcta requiere identidad/PKI, rotación, amenazas y políticas de confianza no disponibles en este proyecto. | Media-baja; peligro de recrear estándares maduros de forma incompleta. | Diferida; integrar implementaciones existentes sería la dirección futura. |
| C. Ledger append-only/Merkle para auditoría | Transparencia de logs y estructuras Merkle ayudan a detectar reescritura/eliminación, pero el objetivo de esta iteración es consumo offline, no servicio distribuido ni prueba de inclusión. | Media; exige almacenamiento, pruebas de consistencia y gobernanza de retención. | Diferida porque no resuelve la semántica de confianza y añade arquitectura que el prototipo no necesita. |

## Relación con estándares y sistemas

W3C PROV ofrece vocabulario de entidades, actividades y agentes: el esquema local es una simplificación no interoperable. MLflow ofrece tracking, artefactos y relaciones de lineage; este ejercicio no compite con su almacenamiento, sólo prueba que un paquete exportado conserve consistencia local. SLSA define provenance de build y recomienda verificar identidad del builder, firmas y parámetros contra expectativas; este MVP no ejecuta esos controles. in-toto representa pasos de supply chain y verifica su cumplimiento con layout y firmas. TUF administra metadatos firmados, roles, expiración y umbrales para distribuir artefactos con seguridad. RFC 8785 especifica canonicalización interoperable JSON; la función incluida es deliberadamente pequeña y no pretende ser implementación JCS.

## Conclusión de novedad

Clasificación: integración de ingeniería y auditoría adversarial sobre una propuesta interna existente. La contribución es un caso ejecutable con negativos explícitos y una regla de confianza delimitada; no se afirma algoritmo científico novedoso. Prior art externo cubre ampliamente firmas, provenance y distribución segura.
