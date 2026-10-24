# Colombia: habilitación de datos y fronteras de uso

Corte 23-10-2026. Esta ficha es una guía de diseño con fuentes oficiales, no un dictamen para una entidad/producto concreto. Referencias completas en [sources.json](sources.json).

## Marco que debe clasificarse antes de integrar

- **Ley 1581 de 2012 [S:law1581]:** finalidad, autorización y excepciones, seguridad y derechos. Un dato es personal si está vinculado o puede asociarse a una persona determinable; IP/ID vinculados a un expediente se tratarán como personales en este diseño. Los biométricos son sensibles y su tratamiento tiene reglas específicas. No se traslada sin análisis el régimen general a toda base financiera.
- **Ley 1266 de 2008 [S:law1266]:** régimen especial de información financiera/crediticia, con notas y modificaciones en el texto consultado. Identificar fuente, operador y usuario, condiciones de consulta/reporte y atención de correcciones. Una finalidad antifraude no da acceso libre a un buró.
- **Ley 2300 de 2023 [S:law2300]:** en cobranza, controlar canales autorizados, horarios, periodicidad y contacto a terceros conforme al ámbito y excepciones aplicables. La ubicación de un cliente no sustituye esos controles.
- **Circular SIC 002 de 2024 [S:sic-ai]:** el uso de IA no elimina obligaciones de tratamiento. Documentar riesgos y medidas del sistema que procesa datos personales.

Las cuatro referencias no constituyen inventario exhaustivo de SIAR/SARC, SARLAFT, consumidor financiero, ciberseguridad, firma o reglas de producto. Su aplicación exige clasificar el caso y las disposiciones vigentes; el diseño no acredita cumplimiento integral SFC/IFRS 9.

## Matriz operativa propuesta para habilitar una señal

| Control de diseño propio | Pregunta de liberación | Evidencia a conservar |
|---|---|---|
| Necesidad y finalidad | ¿Qué riesgo/decisión concreta requiere esta precisión y frecuencia? | Ficha de señal, alternativa menos intrusiva y dueño |
| Ámbito y habilitación | ¿Qué régimen aplica y cuál es la autorización o excepción específica? | Evaluación jurídica y versión de aviso/autorización aplicable |
| Permiso técnico | ¿La plataforma permite el acceso y con qué alcance? | Estado de permiso; no inferir autorización amplia desde un clic del SO |
| Rol y terceros | ¿Qué proveedor recibe qué campos y para qué? | Contrato, encargados/subprocesadores y flujos de comunicación |
| Transferencia/transmisión | ¿Cómo se caracteriza el flujo nacional/internacional? | Revisión específica por roles, destino y condiciones; no equipararlas |
| Conservación y acceso | ¿Quién necesita el dato bruto, derivado o agregado, y hasta cuándo? | Política por categoría, controles de acceso, borrado y excepciones de conservación |
| Decisión admisible | ¿Se usa para fraude, crédito, marketing o contacto? | Lista de usos permitidos y pruebas por finalidad |
| Derechos y atención | ¿Cómo se corrige una fuente y se revisa una decisión? | Ruta operativa, trazabilidad de reclamaciones y respuesta |
| Evaluación | ¿Aporta beneficio sin daño desproporcionado por segmento? | Validación temporal, errores y alternativa accesible |

Esta tabla es nuestra propuesta de gobierno; no se presenta como transcripción de un artículo legal.

## Caso IP frente a ubicación precisa

Una IP puede observarse técnicamente sin abrir el diálogo de geolocalización; eso no elimina la revisión de tratamiento. La API de geolocalización requiere permiso de plataforma y condiciones del entorno [S:w3c]. La autorización de plataforma y la habilitación para uso bancario son controles distintos. Geolocalización no se clasifica automáticamente en este documento como biometría ni como dato siempre sensible: se evalúa contexto, granularidad e inferencias.

Ruta propuesta ante `permission_denied`: continuar con una alternativa de verificación apropiada o dejar pendiente la etapa que realmente requiera evidencia, explicando el motivo. No asumir fraude ni sancionar por defecto la negativa. Una condición necesaria para un producto debe justificarse específicamente, no derivarse de que un SDK ofrece la señal.

## Cobranza y trazabilidad de permisos

Separar autorizaciones de seguridad, mercadeo, conexión financiera y contacto de cobranza. Usar un motor central de elegibilidad de contacto antes de cada envío, incluidos terceros y campañas concurrentes; registrar intento, contacto efectivo, acuerdo y pago como eventos diferentes. La regla vigente debe verificarse antes del despliegue y ser versionable, no una constante dispersa en diez campañas.

El catálogo propone expresamente no usar GPS para ubicar familiares, inferir rutas personales o eludir la negativa de contacto. Validar datos del acreedor, obligación, saldo conciliado y canal antes de mostrar información de deuda. El canal autorizado no prueba quién está al otro lado; evitar revelar deuda a terceros por error.

## Separación de finalidad dentro de la plataforma

Un dato que ayudó a detectar ATO no entra automáticamente en un score de PD. Una queja no es un predictor adverso para penalizar al cliente. El modelo de fraude tampoco debe reaprovechar biometría para marketing. Estas son fronteras del diseño: las listas de usos se validan en el servicio de variables y en la liberación del modelo, no solo en la interfaz del formulario.
