# Brecha residual: ejecución, siniestro y pérdida de garantías

**Corte de evidencia:** 2026-11-11. **Estado:** companion reproducible de enlace administrativo disponible; no hay outcomes públicos enlazados de reclamación y pago.

## Aplicación pública ya realizada

El [companion SECOP II de garantías y obras](observed-secopsurety-works-link/README.md) consulta los conjuntos oficiales CCE `gjp9-cutm` y `jbjy-vk9h`, aplica `tipo_de_contrato='Obra'` y enlaza por `id_contrato` en memoria. En el corte identificó 50.154 IDs únicos de obras, 48.949 filas de garantía de todos los tipos, 4.584 filas enlazadas a obras y 1.076 IDs de obra con al menos una fila. Esto es cobertura de coincidencia entre endpoints, no cobertura jurídica ni ejecución de una garantía.

## Brecha que sigue abierta

El conjunto de garantías no informa si una póliza fue llamada, la reclamación aceptada, el valor pagado, el recuperado ni la pérdida neta. Los estados administrativos y subtipos incompletos no definen el evento de pérdida; puede haber múltiples filas o revisiones por contrato y no hay clave seleccionada para deduplicar pólizas. El dataset de sanciones SECOP puede aportar señales administrativas puntuales, pero no es un inventario completo de siniestros de aseguradoras.

Para estimar `P(call)` o severidad se necesitan: identificador/versionado de póliza; tipo de amparo, obligación y periodo de cobertura; contrato y contratista seudonimizados; evento que origina la reclamación y decisión jurídica; valores reclamado, aceptado, pagado, recuperado y costos; fecha de notificación, desarrollo y cierre; y exposición/obligación garantizada. Se requieren además permisos, conciliación contable/jurídica, reglas para revisiones, cohorte temporal y validación independiente.

Sin esos datos no se valida el modelo de pérdidas de garantía ni riesgo de contraparte. El companion público debe permanecer como diagnóstico de linkage y calidad de registros.
