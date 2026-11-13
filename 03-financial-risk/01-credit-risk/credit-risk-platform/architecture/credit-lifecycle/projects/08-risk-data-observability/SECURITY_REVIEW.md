# Revisión adversarial · Observabilidad de datos, etiquetas y modelos

**Estado:** modelo de amenazas y plan de pruebas, no pentest ejecutado. El activo a proteger es la integridad de `MonitoringAssessment` y sus efectos posteriores. La revisión cubre entrada de cliente, fuente/proveedor, decisión/política, intervención humana y registro de estado según el alcance del proyecto.

El atacante de laboratorio puede controlar atributos y secuencias sintéticas, disponer de un teléfono de prueba o aportar un archivo ficticio. No se presume comprometido todo el banco: cada escenario identifica qué supuesto se debilita. Los casos legítimos de contraste incluyen cambio de teléfono/dispositivo, redes compartidas, accesibilidad, falta de cobertura y error operacional.

## Cuatro escenarios

| ID | Escenario | Supuesto que podría fallar | Control a evaluar | Prueba defensiva propuesta |
|---|---|---|---|---|
| OBS-A1 | Envenenamiento de etiquetas | Alertas o revisiones se convierten en fraude/default confirmado sin adjudicación. | Taxonomía, maduración y origen de label; aprobados y alertados evaluados con diseño apropiado. | Inyectar alertas positivas sin desenlace; el entrenamiento no las toma como verdad confirmada. |
| OBS-A2 | Feature con información futura | Una señal posterior al desembolso hace parecer excelente el modelo histórico. | Doble fecha y snapshot al corte; pruebas de fuga. | Variable disponible después de la decisión queda fuera del snapshot de laboratorio. |
| OBS-A3 | Mejora aparente por cobertura selectiva | Un cambio excluye casos difíciles y mejora la métrica de los restantes. | Denominador poblacional y comparación de cobertura/madurez por canal. | Versión simulada falla en un subgrupo; se reporta abandono de cobertura además de desempeño. |
| OBS-A4 | Cambio remoto sin versión | Una misma API devuelve otra semántica y el monitor solo mira la estructura JSON. | Registro de versión/semántica, shadow y diagnóstico antes de recalibrar. | Payloads válidos de esquema con score invertido o concepto cambiado; no se liberan por compatibilidad sintáctica. |

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
