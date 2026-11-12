# Experimentos propuestos · Formalización y condiciones precedentes

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## FORM-01 · Cambio de oferta después de aceptar

**Hipótesis falsable:** Enlazar aceptación a versión exacta evita ejecutar términos diferentes a los aceptados.

**Estimando, objetivo o invariante:**

\[
accepted\_version=execution\_offer\_version
\]

**Diseño y comparador:** Variar monto, plazo, moneda, tasa y cuenta destino; conservar original e introducir cambios antes/después de aceptación y firma. Diferenciar cambios que requieren nueva aceptación según regla de producto.

**Métricas e incertidumbre:** Paquetes incoherentes detectados, reprocesos y falsos bloqueos.

**Qué refuta la propuesta:** Una secuencia que permita términos incompatibles con la versión aceptada invalida el control.

**Revisión adversarial:** escenarios FORM-A1, FORM-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Corpus de paquetes y validación determinista de referencias/versiones.

## FORM-02 · Autenticidad, integridad y soporte

**Hipótesis falsable:** Conservar un span/hash no detecta por sí solo un documento falso o una afirmación mal interpretada.

**Estimando, objetivo o invariante:**

\[
claim\_supported=integrity\land source\_scope\land semantic\_support
\]

**Diseño y comparador:** Documentos de laboratorio ficticios y marcados como no válidos: texto coherente sin emisor, campo cambiado, concepto de ingreso equivocado y corrección posterior. Separar tres capas del predicado.

**Métricas e incertidumbre:** Afirmaciones sin soporte aceptadas, abstención y evidencia alternativa requerida.

**Qué refuta la propuesta:** Descartar la conclusión de autenticidad si solo se comprobó igualdad con el archivo subido.

**Revisión adversarial:** escenarios FORM-A2, FORM-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Suite documental defensiva que referencia el pipeline de evidencia existente.

## FORM-03 · Garantía y vigencia antes de efecto

**Hipótesis falsable:** Una condición satisfecha al emitir la oferta puede dejar de estar vigente antes de ejecutar.

**Estimando, objetivo o invariante:**

\[
valid\_at(t_{execution})\land conditions\_version=policy\_version
\]

**Diseño y comparador:** Estados sintéticos de condición pendiente/cumplida/expirada/controvertida y autorización concurrente. Los criterios jurídicos se proporcionan como reglas de ejemplo, sin inferirlos del laboratorio.

**Métricas e incertidumbre:** Autorizaciones sin condición vigente, esperas y discrepancias por revisión.

**Qué refuta la propuesta:** No aceptar un paquete si no puede reconstruirse quién validó la condición y con qué evidencia al tiempo del efecto.

**Revisión adversarial:** escenarios FORM-A3, FORM-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Contrato de condiciones y reporte de precondiciones por caso.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
