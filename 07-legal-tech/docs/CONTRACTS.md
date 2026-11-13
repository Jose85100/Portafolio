# Contratos de evidencia — especificación

Son contratos propuestos; todavía no hay un validador implementado.

## Documento y fragmento

| Campo | Regla |
|---|---|
| document_id / version_id / fragment_id | Identidad estable, versión inmutable y pasaje localizable |
| canonical_url / retrieved_at / sha256 | Procedencia, fecha de captura UTC y hash del archivo original |
| issuer / jurisdiction / territory / source_type | Autoridad, jurisdicción, territorio y clase de documento separados |
| publication_date / effective_from / effective_to | Fechas distintas; extremos desconocidos permanecen nulos |
| observed_at / available_at | Cuándo se observó y desde cuándo estuvo disponible en el sistema |
| temporal_status | verified, disputed o unknown, con evidencia y revisor |
| locator / text / parent_id | Artículo, inciso, página o párrafo y contexto superior |
| extraction_method / ocr_quality | Método y calidad estimada; errores críticos exigen cotejo visual |
| access_scope / tenant_id / classification | Público o privado; ámbito explícito, nunca permiso por defecto |
| relations | Modificación o cita con pasaje probatorio, fecha y revisión |

Hash prueba integridad respecto del snapshot, no autenticidad del emisor, vigencia ni verdad del contenido. Las citas usan offsets del texto normalizado y localizador del original; conservar ambas versiones.

## Consulta

`query_id`, pregunta, propósito, fecha de hechos, fecha de corte de conocimiento, territorio, jurisdicción candidata, régimen, identidad y ámbitos autorizados. Preguntar por campos materiales ausentes. No inferir una fecha de notificación desde la fecha de expedición.

## Respuesta

Cada `claim` incluye texto, tipo (hecho, cita, inferencia o recomendación), `evidence_ids`, pasajes, localizadores, alcance temporal, limitaciones y estado de revisión. Incluir fuentes contrarias materiales. Citas literales deben coincidir con el snapshot; una paráfrasis no se marca como cita literal.

Estados permitidos: `draft`, `needs_context`, `needs_review`, `abstain`, `reviewed`. El modelo solo puede producir los cuatro primeros; `reviewed` exige identidad y decisión de un revisor autorizado. La validación de soporte puede clasificar `supported`, `contradicted`, `insufficient`: no equivale a dictamen de corrección jurídica.

Una afirmación jurídica material sin soporte bloquea la entrega como respuesta conclusiva. La falta de fuente no se resuelve con conocimiento paramétrico del modelo. Conflictos materiales se muestran explícitos para revisión.
