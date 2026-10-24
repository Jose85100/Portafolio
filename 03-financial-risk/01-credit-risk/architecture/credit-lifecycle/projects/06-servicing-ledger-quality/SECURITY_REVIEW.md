# Revisión adversarial · Calidad del ledger y estado de la obligación

**Estado:** modelo de amenazas y plan de pruebas, no pentest ejecutado. El activo a proteger es la integridad de `LoanStateSnapshot` y sus efectos posteriores. La revisión cubre entrada de cliente, fuente/proveedor, decisión/política, intervención humana y registro de estado según el alcance del proyecto.

El atacante de laboratorio puede controlar atributos y secuencias sintéticas, disponer de un teléfono de prueba o aportar un archivo ficticio. No se presume comprometido todo el banco: cada escenario identifica qué supuesto se debilita. Los casos legítimos de contraste incluyen cambio de teléfono/dispositivo, redes compartidas, accesibilidad, falta de cobertura y error operacional.

## Cuatro escenarios

| ID | Escenario | Supuesto que podría fallar | Control a evaluar | Prueba defensiva propuesta |
|---|---|---|---|---|
| SERV-A1 | Pago aparente sin confirmación | Una promesa, comprobante o mensaje se convierte en saldo pagado. | Ledger y conciliación de efectivo como evidencia; soporte aportado abre investigación. | Comprobante ficticio y promesa sin movimiento conciliado; no cerrar deuda como pagada. |
| SERV-A2 | Corrección que contamina el pasado | Una modificación borra la evidencia o altera features históricas sin disponibilidad al corte. | Bitemporalidad y ajustes versionados con atribución. | Corrección posterior en pagos sintéticos; snapshots anteriores se mantienen reproducibles. |
| SERV-A3 | Errores compensados entre cuentas | Dos imputaciones opuestas dejan el agregado correcto y obligaciones incorrectas. | Conciliación por referencia/titular/moneda/valor, no solo totales. | Intercambiar abonos entre dos préstamos ficticios y exigir discrepancias individuales. |
| SERV-A4 | Reestructuración o novedad indebida | Un cambio administrativo altera mora/saldo sin autoridad o evidencia de acuerdo. | Workflow de novedad con atribuciones y documento/condiciones pertinentes. | Evento sintético con rol no autorizado; debe conservarse intento y no cambiar obligación. |

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
