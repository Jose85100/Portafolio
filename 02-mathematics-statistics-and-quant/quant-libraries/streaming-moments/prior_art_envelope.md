# Matriz de literatura y selección — 3 noviembre 2026

Fuentes consultadas directamente el 3-nov-2026. Esta búsqueda cubre estándares de representación/hash y documentación del runtime; no es una búsqueda sistemática de literatura sobre proveniencia o sistemas de auditoría.

|Fuente|Problema/supuestos|Método/evidencia primaria|Diferencia verificable aquí|
|---|---|---|---|
|[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)|Representación JSON determinista para hashing/firmas; restricciones precisas sobre serialización|JSON Canonicalization Scheme (JCS), texto del estándar abierto|La implementación **no** implementa JCS; se limita a JSON ordenado de Python y declara no interoperabilidad byte-exacta|
|[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html)|Formato de intercambio JSON interoperable; no define por sí solo firma o canonicalización|Estándar JSON abierto|Sobre local con campos de disponibilidad de diagnósticos; no altera el número contrato V1|
|[NIST FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4)|Funciones hash SHA-2; salida digest|Estándar SHA, especifica SHA-256|Usamos SHA-256 como detección de cambios, sin afirmar autenticidad ni firma|
|[Python 3.12 json](https://docs.python.org/3.12/library/json.html)|Serialización/deserialización en runtime fijado|API `json.dumps`, `sort_keys`, `separators`|La configuración concreta es parte de la codificación local del digest|
|[Python 3.12 hashlib](https://docs.python.org/3.12/library/hashlib.html)|Hash criptográfico en runtime fijado|API `sha256`|Hash sobre bytes ASCII del payload y JSON UTF-8 del envelope|
|Welford (1962), Chan et al. (1983), Higham (2002)|Cálculo incremental y estabilidad de momentos|Fuentes preservadas del programa acumulativo|La ecuación del estimador no cambia; este trabajo añade metadatos laterales de auditoría|

## Tres ideas candidatas

|Candidata|Brecha/diferencia|Valor y evidencia|Viabilidad/decisión|
|---|---|---|---|
|A. Sobre Python lateral con nullable status|V1 omite diagnósticos históricos; C++ no debe interpretar contador reiniciado como cero|Hace explícito tracked/partial/unknown, prueba mutación|Seleccionada: reutiliza wire y C++ existente; límites verificables en un incremento|
|B. Cambiar `MOMENTS_V1` a `MOMENTS_V2` y modificar Python+C++|Podría transportar campos estructurados en el protocolo|Mayor acoplamiento/compatibilidad y requiere versionar ambas APIs|Aplazada: cambia contrato compartido sin necesidad demostrada|
|C. Firmar manifiesto con clave o cadena de transparencia|Atendería autenticidad/auditoría organizacional|Exige gestión de claves, identidad y un threat model|Aplazada: infraestructura ausente; no fingir seguridad|

Clasificación defendible: adaptación de ingeniería / auditoría semántica. No es fórmula nueva, contribución estadística ni prueba de procedencia. Fuentes: `referencias.bib`; cobertura primaria limitada a estándares/formato/hash.
