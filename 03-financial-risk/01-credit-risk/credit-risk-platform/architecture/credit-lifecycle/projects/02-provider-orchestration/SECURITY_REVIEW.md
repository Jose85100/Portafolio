# Revisión adversarial · Orquestación de proveedores, costo y resiliencia

**Estado:** modelo de amenazas y plan de pruebas, no pentest ejecutado. El activo a proteger es la integridad de `QueryPlan/ProviderOutcome` y sus efectos posteriores. La revisión cubre entrada de cliente, fuente/proveedor, decisión/política, intervención humana y registro de estado según el alcance del proyecto.

El atacante de laboratorio puede controlar atributos y secuencias sintéticas, disponer de un teléfono de prueba o aportar un archivo ficticio. No se presume comprometido todo el banco: cada escenario identifica qué supuesto se debilita. Los casos legítimos de contraste incluyen cambio de teléfono/dispositivo, redes compartidas, accesibilidad, falta de cobertura y error operacional.

## Cuatro escenarios

| ID | Escenario | Supuesto que podría fallar | Control a evaluar | Prueba defensiva propuesta |
|---|---|---|---|---|
| PROV-A1 | Teléfono preparado para una identidad reclamada | Posesión de número/OTP se promueve a identidad civil por una cadena de proveedores. | Tipar phone_possession_verified separado de identity_link_verified; la evidencia insuficiente sigue pendiente. | Proveedor simulado confirma posesión pero no vínculo; oferta no avanza por ese solo pase. |
| PROV-A2 | Aprobación por degradación o fuente ausente | Un timeout o falta de cobertura elimina controles necesarios. | Estado unavailable distinto de passed; plan alternativo autorizado con capacidad real. | Forzar caída individual/compartida y verificar que no surja aprobación implícita. |
| PROV-A3 | Respuesta duplicada o no confiable | Un resultado se atribuye a otro caso, fuente, versión o sesión. | Autenticar el canal/callback, correlacionar caso/sesión y rechazar semántica desconocida. | Eventos ficticios duplicados, antiguos y con case_id diferente; sin llamadas a proveedores. |
| PROV-A4 | Independencia falsa de varias verificaciones | Tres señales favorables dependen del mismo teléfono, documento o fuente equivocada. | Linaje por hecho verificado y análisis de fallo conjunto; no contar evidencia repetida como independiente. | Mismo atributo falso alimenta tres respuestas simuladas; medir si cambia indebidamente la conclusión. |

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
