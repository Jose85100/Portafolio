# Proveedores puntuales por etapa y tipo de información

24 candidatos, consulta pública al 23-10-2026. Las capacidades son **declaraciones del proveedor**, no ensayos independientes ni integraciones existentes. Las ocho primeras filas amplían el contexto de la revisión de fraude previa; las otras dieciséis agregan opciones. No se contactó ni contrató a ninguno. Fuentes por ID en [sources.json](sources.json).

| Proveedor | Producto / capacidad documentada | Etapa | Información/interfaz conceptual | Pregunta crítica | Fuente | Localización |
|---|---|---|---|---|---|---|
| iProov | Vida y comparación facial | Captura/identidad | Captura y referencia → resultado biométrico | Versión SDK, presentación/inyección y accesibilidad | S:iproov | Global; cobertura y condiciones Colombia no verificadas |
| Truora | Document and Face Validation | Identidad/originación | Documento/rostro → verificaciones | Documentos colombianos concretos, calidad y respuesta inconclusa | S:truora | Oferta regional; confirmar documento/canal/contrato |
| SEON | Fraud API | IP/dispositivo/contacto | Email/teléfono/IP/SDK → señales y score | Señales efectivamente disponibles, calibración y dependencia | S:seon | Global; no se presume cobertura uniforme |
| Socure | Sigma Synthetic Fraud | Identidad sintética | Atributos de identidad → score | Mercado/fuentes admitidos y calibración local | S:socure | Localización Colombia no verificada |
| BioCatch | Behavioral Biometrics | Sesión/ATO/coerción | Telemetría conductual → señales de riesgo | Consentimiento, accesibilidad, muestra adjudicada y valor incremental | S:biocatch | Confirmar canal/plataforma/contrato |
| Feedzai | RiskOps | Fraude/operación | Señales/eventos → decisiones/casos | Módulos, límites de llamadas, versiones y exportación | S:feedzai | Confirmar módulos y operación local |
| Persona | Workflows | Orquestación de identidad | Eventos/estados → tareas/flujo | Orden, duplicados, pendientes y disponibilidad de verificaciones | S:persona | No equivale a motor crediticio completo |
| Belvo | Income Verification | Ingresos y datos conectados | Cuenta conectada → perfil de ingresos | País/banco/producto y titularidad; distinguir crédito/transferencia | S:belvo | No se afirma producto de ingresos disponible en todo Colombia |
| Fingerprint | Smart Signals | Dispositivo/IP/app | SDK/evento → señales e identificador | Web/iOS/Android tienen señales distintas; SDK y precisión | S:fingerprint | Confirmar plataforma, plan y cobertura |
| MaxMind | GeoIP / datos de anonimización | IP y región aproximada | IP → red, región y atributos según producto | Radio/fecha y redes móviles; evaluar Colombia | S:maxmind | No extrapolar exactitudes publicadas para otros países |
| IPinfo | Geolocation / Privacy Detection | IP/ASN/VPN/proxy | IP → geodatos y categorías de privacidad | Producto, actualización y discrepancias frente a verdad local | S:ipinfo | Datos de IP; no ubicación GPS del usuario |
| LexisNexis Risk Solutions | ThreatMetrix | Identidad digital/dispositivo | Contexto digital → señales/decisión de riesgo | Cobertura, dependencias, razones y replay | S:lexis | Confirmar contrato y mercado; no identidad civil por sí sola |
| Prove | Prove Identity | Teléfono/identidad | Teléfono/contexto → verificación/riesgo | Operadores/mercado, posesión vs identidad y fallos | S:prove | Cobertura telco Colombia pendiente |
| Telesign | Phone ID SIM Swap | Telco/ATO | Número → atributo SIM swap si habilitado | Operador/país y habilitación del complemento; tiempo y semántica | S:telesign | Documento exige confirmar mercados soportados |
| TransUnion Colombia | Originación, CreditVision / Collections Score | Buró/portafolio/cobranza | Consulta habilitada → historia/variables/analítica | Población, desfase, reclamaciones y condiciones de consulta | S:tu; tu-collections | Fuente oficial colombiana |
| DataCrédito Experian | Soluciones de originación / Perfil / CobraYa | Buró/originación/cobranza | Información crediticia habilitada → reportes/servicios | Producto concreto, derechos, cobertura y estado de reporte | S:experian | Fuente oficial colombiana |
| FICO | FICO Platform | Decisión/cupo/clientes/cobranza | Datos/modelos/políticas → decisión | Producto/módulo, reglas, despliegue y validación interna | S:fico | Plataforma global; no score colombiano listo por defecto |
| Provenir | Decision Intelligence Platform | Orquestación y decisión | Datos/proveedores/modelos → flujo/decisión | Versionado, rutas manuales, exportación, auditoría y TCO | S:provenir | No asumir marketplace contratado ni datos habilitados |
| Mambu | Core/lending APIs y ledger | Administración de préstamo | Producto/cuenta/eventos → obligación y servicio | Convenciones de interés, calendario, imputación, contabilidad e integración local | S:mambu | Confirmar localización y producto |
| Temenos | Core / módulos de originación y collections | Core/LOS/cobranza | Expediente/producto/eventos → administración | Seleccionar familia de producto, geografía y adaptadores | S:temenos | Fuente de módulos consultada es de credit unions/community; Colombia pendiente |
| Certicámara | Certificados de firma digital | Formalización | Evidencia/identidad → certificado/servicio contratado | Tipo de firma, certificado, revocación y expediente jurídico | S:certicamara | Fuente oficial de oferta colombiana |
| Deceval | Pagarés desmaterializados | Instrumentación/custodia | Solicitud/instrumento → registro/administración | Modelo de conexión, roles y requisitos jurídicos por producto | S:deceval | Servicio publicado por BVC; confirmar operación contractual |
| ACH Colombia | Transferencias ACH / PSE | Desembolso según riel / recaudo | Orden habilitada → estado y referencia | Servicio por dirección de fondos, idempotencia, horarios y conciliación | S:ach | PSE es recaudo, no motor de aprobación ni desembolso universal |
| Finvi | Katabat | Cobranza y gestión de interacción | Cartera/canal → tratamientos y seguimiento | Localización jurídica, canales, concurrencia, acuerdos y quejas | S:katabat | Oferta global; reglas Colombia pendientes |

## Qué compra cada familia

- **Enriquecimiento IP/dispositivo:** señales y contexto. No entrega el expediente bancario del cliente ni una decisión crediticia validada.
- **Identidad/biometría:** verificar una evidencia y vínculo bajo cobertura; identidad real puede coexistir con insolvencia, coerción o mula.
- **Telco:** atributos de número/posesión/cambios bajo acceso específico; no se presupone acceso a mensajes o ubicación de antenas.
- **Buró:** historia y variables cubiertas por reporte/contrato; no equivale a todos los flujos bancarios ni reemplaza corregir información controvertida.
- **Datos financieros conectados:** señales de cuentas cubiertas y habilitadas; no todos los bancos, mercados ni cuentas del usuario.
- **Motor de decisiones/LOS:** política y orquestación, no una habilitación automática para captar los datos de todos sus conectores.
- **Core/LMS:** administración/ledger de obligaciones, no calibración validada de PD ni prevención integral de fraude.
- **Firma/pagaré/pagos:** servicios distintos; separar identidad, aceptación contractual, instrumentación, ejecución y liquidación.
- **Cobranza:** gestión de casos/tratamientos, subordinada a saldo correcto y reglas de contacto aplicables.

## Combinaciones de referencia, sin ranking

**Banco con core existente:** mantener core/contabilidad; introducir una capa propia de decisiones y adaptadores. Evaluar buró colombiano, proveedor de identidad, IP/dispositivo y firma/pagaré por requerimiento; conservar límites y ledger. Telesign/Prove solo si la cobertura telco y el uso están confirmados.

**Prestamista con plataforma acotada:** backend modular y workflow durable para verificación/revisión; proveedor de identidad según documento/canal; buró habilitado; fuente de ingreso donde realmente cubra población; core/LMS propio o contratado con conciliación. Empezar con reglas y logit antes de añadir red profunda o múltiples scores redundantes.

**Operación con múltiples productos y alto volumen:** evaluar FICO/Provenir o un motor interno con gobierno equivalente, workflow por eventos y adaptadores intercambiables. Feedzai/BioCatch/ThreatMetrix pueden cubrir necesidades de fraude distintas de las del motor de crédito; demostrar aporte incremental y dependencia antes de combinar.

Estas son hipótesis de arquitectura, no recomendaciones de compra. Evitar una lista que contrate varios productos por capa solo para llenar el diagrama.

## Costo total y evaluación

\[
TCO=C_{integracion}+C_{fijo}+N_{consultas}c_{consulta}
+N_{reintentos}c_{reintento}+N_{revisiones}c_{revision}
+C_{operacion}+C_{auditoria}+C_{salida}.
\]

Definir qué se factura por intento, sesión, persona o resultado, y si hay cargos mínimos, SDK, retención o soporte. No hay precios contrastados ni SLA contratados en esta entrega.

Evaluar sobre el mismo universo/corte y presupuesto: cobertura útil, errores por amenaza y segmento, beneficio económico incremental, fricción, latencia p50/p95/p99, indisponibilidad, tiempos de revisión, trazabilidad y portabilidad. Un score de proveedor no se presume probabilidad; calibrarlo o usarlo como señal con evaluación temporal.

## Preguntas que debe cerrar un RFI/RFP

1. ¿Producto y versión exactos, países/documentos/operadores/bancos y señales por plataforma? Pedir matriz de cobertura y evidencia sobre una muestra representativa.
2. ¿Qué campos se captan/transmiten, con qué roles, finalidades, subprocesadores, ubicaciones y conservación? Confirmar flujos internacionales por su figura aplicable.
3. ¿Qué controla el banco y qué cambia remotamente el proveedor? Exigir señales/versiones/razones exportables y tratamiento de versión desconocida.
4. ¿Cómo se autentican callbacks, manejan duplicados, estados pendientes y reintentos? ¿Qué consulta confirma un pago incierto?
5. ¿Cuál es el rendimiento incremental frente al baseline al mismo costo/capacidad, sin copiar cifras comerciales de otra población?
6. ¿Qué alternativa existe ante negativa de permiso, discapacidad, documento no soportado o caída compartida?
7. ¿Puede migrarse fuera del servicio y reproducirse la decisión histórica dentro de obligaciones de conservación? Exportar trazabilidad no exige conservar medios brutos indefinidamente.
