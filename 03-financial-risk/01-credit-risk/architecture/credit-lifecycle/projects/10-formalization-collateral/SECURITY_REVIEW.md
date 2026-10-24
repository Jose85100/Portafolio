# Revisión adversarial · Formalización y condiciones precedentes

**Estado:** modelo de amenazas y plan de pruebas, no pentest ejecutado. El activo a proteger es la integridad de `FormalizationReadiness` y sus efectos posteriores. La revisión cubre entrada de cliente, fuente/proveedor, decisión/política, intervención humana y registro de estado según el alcance del proyecto.

El atacante de laboratorio puede controlar atributos y secuencias sintéticas, disponer de un teléfono de prueba o aportar un archivo ficticio. No se presume comprometido todo el banco: cada escenario identifica qué supuesto se debilita. Los casos legítimos de contraste incluyen cambio de teléfono/dispositivo, redes compartidas, accesibilidad, falta de cobertura y error operacional.

## Cuatro escenarios

| ID | Escenario | Supuesto que podría fallar | Control a evaluar | Prueba defensiva propuesta |
|---|---|---|---|---|
| FORM-A1 | Imagen de documento alterada | El OCR extrae datos coherentes de una evidencia cuyo contenido o retrato fue modificado. | Separar extracción, autenticidad y vínculo con persona; fuente corroborante habilitada y revisión de inconclusos. | Documento enteramente ficticio marcado NO VÁLIDO con campos contradictorios; evaluar la capa que debe abstenerse. |
| FORM-A2 | Documento de otra persona o reutilizado | Una imagen auténtica se aporta fuera de su sujeto/sesión/contexto válido. | Identidad reclamada, titular de evidencia, captura y sesión enlazadas; no pase por archivo conocido. | Dos identidades de prueba y referencia cruzada; sin fotos ni documentos de terceros reales. |
| FORM-A3 | Paquete firmado distinto al ejecutado | La firma o aceptación corresponde a una versión y la operación usa otra. | Integridad, versión de oferta y condiciones coherentes; autenticidad/validez jurídica se evalúan aparte. | Versiones sintéticas con monto/plazo distintos; impedir readiness del paquete incoherente. |
| FORM-A4 | Instrucción dentro del documento | El texto intenta convertir al extractor en aprobador o invocar una herramienta. | Tratar archivo como datos, extractor sin permisos de pago/aprobación y validación de soporte. | Texto ficticio que pide aprobar; verificar que solo produzca candidatos de campos o abstención. |

## Encadenamiento y rutas alternativas

Ejecutar también un escenario combinado: una señal aparentemente favorable y otra faltante/tardía, junto con la ruta de revisión o degradación. Un control fuerte no compensa necesariamente otro omitido; la decisión debe preservar qué hecho verificó cada control. No multiplicar evidencia correlacionada como si fueran identidades independientes.

El mapa transversal de [THREAT_MODEL.md](../THREAT_MODEL.md) distingue identidad reclamada, titularidad nominal, control del teléfono, posesión de evidencia, vínculo con la persona, intención/voluntad y destino de fondos. Cada etapa conserva su alcance; controlar un canal o presentar un documento no habilita por sí solo el crédito ni el efecto de pago.

## Protocolo de laboratorio

1. Autorizar alcance, activos y ambiente; trabajar con entidades, teléfonos de prueba y documentos enteramente ficticios y marcados, sin documentos reales de terceros.
2. Congelar baseline/política y reservar familias de escenarios de test; describir capacidad del actor y condiciones iniciales.
3. Ejecutar cada caso y un control legítimo comparable; conservar solicitudes, estado previo, respuesta, transición, razones y efecto simulado.
4. Verificar que el fallo genera bloqueo de la transición inválida, evidencia pendiente o revisión según el contrato, sin convertir inconcluso en fraude ni error en pase.
5. Registrar residuo de riesgo, costo, fricción, falsos positivos y punto exacto de fallo. Si se corrige, repetir el caso y sus vecinos legítimos.

Estas son pruebas propuestas. No contienen procedimientos para falsificar una cédula, activar una línea a nombre ajeno, extraer modelos o eludir un proveedor real. Los fixtures futuros deben representar el resultado de una manipulación, no facilitar su ejecución fuera del laboratorio.

## Evidencia y criterio de liberación

Guardar `scenario_id`, `case_id`, versión de política/contrato, variante de fixture, resultado esperado, resultado observado y razón de discrepancia. En esta entrega no existe resultado observado. Un caso crítico aceptado por una ruta que debía impedirlo bloquea el avance del prototipo; cero fallos en un conjunto finito no acredita invulnerabilidad.

La revisión de escritorio comprueba coherencia de supuestos y controles. Una prueba técnica posterior y una evaluación institucional independiente tienen alcances diferentes. El proyecto sigue S1 hasta cumplir su contrato de prototipo.
