# Nota teórica: envelope de auditoría

## Pregunta y relación con el contrato

El contrato numérico `MOMENTS_V1` contiene el estado suficiente `(n,e,a,b,Q,i)`, pero al importar a C++ reinicia contadores históricos. No se debe inferir que “cero eventos” significa que nunca hubo eventos: el protocolo no transporta ese dato. Este incremento añade un sobre JSON lateral, sin alterar `MOMENTS_V1` ni la fórmula de varianza.

Para observaciones normalizadas `y_j`, el núcleo conserva

$$n=\sum_j 1,\qquad \bar y=a+b,\qquad Q=\sum_{j=1}^n(y_j-\bar y)^2,$$

con `a` origen, `b` media desplazada y `e` tal que `x=2^e y`. La varianza muestral/poblacional sigue siendo

$$s_d^2=2^{2e}\frac{Q}{n-d},\qquad d\in\{0,1\},\;n>d.$$

Nada de esa igualdad cambia. El sobre lleva la cadena V1 exacta, su hash SHA-256, etiquetas declaradas `source_id` y `partition_id`, una afirmación de partición fija a `declared_unverified`, y tres contadores con estado de disponibilidad.

## Regla de representación de diagnósticos

Sea `C=(c_1,c_2,c_3)` el vector de contadores. Si `state=tracked`, los tres `c_i` son enteros no negativos; un cero explícito significa cero medido. Si `partial`, un subconjunto propio, no vacío, son enteros y los demás son `null`. Si `unknown`, los tres son `null`. Esta es una invariante de tipos/semántica, no un modelo probabilístico.

Se valida el payload V1 antes de envolverlo. El digest de payload es

$$h_p=\operatorname{SHA256}(\operatorname{ASCII}(payload)).$$

Se calcula además `h_e` sobre una codificación JSON local del documento sin `envelope_sha256`, con claves ordenadas y separadores compactos. Esto detecta mutaciones accidentales del payload y metadatos bajo esa misma codificación local. **No** es una firma ni autenticación: quien pueda editar el sobre puede recomputar ambos hashes. La serialización sólo es determinista bajo esta implementación/contrato de Python; no se afirma conformidad JCS/RFC 8785 ni equivalencia byte-a-byte entre lenguajes.

El campo `partition_id` identifica lo que declara el productor. No demuestra que las filas sean disjuntas. Tampoco `source_id` demuestra quién generó los datos. No se incluye `n`/resumen estadístico en los metadatos para no duplicar un estado derivable del payload.

## Hipótesis falsables y propiedades

H1 (software): en 12 estados sintéticos, los bytes exactos del payload, la categoría diagnóstica y los campos de procedencia sobreviven serialize/parse. Umbral fijado: 12/12.

H2 (integridad): cambiar payload o metadatos sin recomputar hashes debe ser rechazado en todos los casos de mutación ensayados. El experimento no prueba resistencia criptográfica ni ataques con capacidad de re-firmar.

Propiedades conservadas: el wire V1 es idéntico; el consumidor C++ existente continúa interpretándolo; `null` no se convierte a cero. Propiedades que no agrega: autenticidad, privacidad, disjunción real, procedencia verificable, completitud de diagnósticos, canonicalización interoperable o validez estadística.

El baseline es otro JSON lateral plano con exactamente los mismos campos esenciales y hashes SHA-256 sobre payload y registro. Los dos caminos llaman al mismo validador semántico y prueban el mismo payload/parsing, status, origen, partición y contadores; no se compara un envelope completo contra una verificación de sólo dos checksums. El benchmark de bytes/tiempo es descriptivo, no constituye hipótesis de superioridad, y mide estas dos implementaciones Python concretas.
