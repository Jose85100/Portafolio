# Capas y alternativas de arquitectura crediticia

No existe una lista universal de «todas las capas»: el producto, el país, el canal y el volumen cambian el diseño. Estas quince responsabilidades cubren el alcance de referencia, desde captación hasta recuperación. Una responsabilidad puede vivir en el mismo proceso que otras. Diagramas en [diagrams/](diagrams/README.md); son diseño S1.

## Quince responsabilidades lógicas

| Capa | Responsabilidad y motores | Entradas → salidas | Decisión/fallo que controla |
|---|---|---|---|
| 01. Producto y apetito | Catálogo de producto, elegibilidad, segmentos, precio y límites | Política aprobada → oferta vigente | Ofrecer un producto fuera del apetito o de su vigencia |
| 02. Canales | App, web, oficina, asesor, aliado y accesibilidad | Interacción → solicitud/canal/origen | Doble expediente, caída y abandono |
| 03. Acceso y sesión | IAM, autenticación, integridad, protección de API y rate limits | Sesión → principal/estado/contexto | Toma de cuenta y bots; login no prueba intención |
| 04. Finalidad y permisos | Aviso, autorizaciones, restricciones, revocación y evidencias | Propósito y fuente → captación habilitada | Reutilización incompatible de datos |
| 05. Expediente/LOS | Workflow, estados, documentos, plazos e idempotencia | Solicitud → expediente y tareas | Aprobar una solicitud incompleta o vencida |
| 06. Evidencia y proveedores | KYC/KYB, listas, buró, ingresos, firma, telco | Respuestas → señales con estado y versión | Convertir timeout/ausencia en aprobado |
| 07. Datos y variables | Calidad, identidad de entidades, doble fecha, snapshots y feature store | Eventos → variables disponibles al corte | Fuga temporal, claves equivocadas, fuente obsoleta |
| 08. Modelos | Fraude, PD, capacidad, LGD/EAD, comportamiento e incertidumbre | Variables → estimación con población/horizonte | Confundir score, probabilidad y decisión |
| 09. Política/optimización | Reglas, precio, cupo, garantías, capacidad de revisión y exposición | Estimaciones → oferta/revisión/decisión motivada | Sumar probabilidades correlacionadas o sobreasignar recursos |
| 10. Revisión y atención | Analista, excepción, explicación, reclamación y doble control | Caso → resolución autorizada | Excepción informal y exclusión sin revisión |
| 11. Formalización | Oferta aceptada, contrato, firma, pagaré y garantías | Consentimiento contractual → instrumento verificable | Confundir clic, firma y título exigible |
| 12. Desembolso/pagos | Cuenta destino, revalidación, ledger, conciliación y reversos | Autorización → efecto confirmado/pendiente | Pago duplicado y reintento ante estado desconocido |
| 13. Administración/LMS | Cronograma, intereses, imputación, extractos, novedades y prepago | Obligación → saldos y eventos conciliados | Mora artificial por error de imputación o calendario |
| 14. Seguimiento/cobranza | Alertas tempranas, contacto, acuerdos, reestructuración y recuperación | Estado de cuenta → tratamiento/resolución | Cobrar saldo no conciliado o tratar mora como fraude |
| 15. Riesgo y gobierno | Cosechas, provisiones, estrés, concentración, validación, seguridad y auditoría | Cohortes/escenarios → decisiones de gobierno | Medir labels inmaduros o desplegar cambios sin control |

Seguridad, privacidad, observabilidad, continuidad y auditoría atraviesan todas las capas. Los logs operativos no son un lago libre de PII. El catálogo de datos y las políticas de acceso deben distinguir expediente, señales, artefactos de modelos y contabilidad.

## A. Plataforma modular con operación síncrona

**Elegir cuando:** equipo pequeño, producto acotado y demanda que cabe en un despliegue simple. Un backend modular mantiene LOS, adaptadores, decisión y tareas con límites claros; el core y fuentes externas conservan sus APIs.

**Contratos:** request_id, case_id, deadline, versión y estado de respuesta. Un timeout externo puede dejar la solicitud pendiente; no prolongar una transacción de base de datos mientras se espera a una API. Guardar una intención y retomar mediante una tarea durable.

**Ventajas:** transacciones locales sencillas, menor carga operacional y replay más fácil. **Costos:** el despliegue es compartido y se requiere aislar consultas pesadas, trabajo documental y recursos de proveedores. Escalar primero workers y colas; no separar servicios por cada caja del diagrama.

## B. Plataforma orientada a eventos y workflows durables

**Elegir cuando:** múltiples productos/canales, verificaciones asíncronas, analistas, firma y pagos con esperas largas. Workflow de crédito con estado durable, bus, outbox, consumidores idempotentes y colas de errores.

**Contratos:** event_id único, aggregate_id, aggregate_version, event_time, available_time, correlation_id y schema_version. Emitir el evento de decisión y su registro de outbox dentro de la misma transacción local. El consumidor registra efecto e idempotencia de forma atómica donde sea posible; el proveedor de pago requiere su propia clave y consulta de estado.

**Ventajas:** aislamiento y recuperación por etapa. **Costos:** duplicación, orden parcial, consistencia eventual y mayor operación. No prometer exactly-once entre entidades. Un desembolso ya liquidado no se «deshace» borrando un evento; cualquier reverso o recuperación es un efecto nuevo con reglas propias.

## C. Core existente con capa de decisión y datos desacoplada

**Elegir cuando:** la entidad conserva un core/LOS probado y necesita modernizar evaluación y monitoreo. Usar adaptadores con semántica explícita, APIs gobernadas y CDC/eventos para analítica, sin escribir directamente en tablas internas del core.

**Contratos:** identificar sistemas de registro por entidad, conciliar totales y saldos, versionar códigos y calendarios. La decisión de crédito se expone como servicio, pero el core sigue siendo dueño de la obligación/ledger. Una réplica analítica con retraso no autoriza un desembolso.

**Ventajas:** modernización incremental. **Costos:** lag, reconciliación, semánticas históricas y riesgo de duplicar saldos. Introducir inicialmente sombra, luego un segmento controlado; no una sustitución total por defecto.

## Comparación para elegir

| Criterio | Modular síncrona | Eventos/workflow | Core + decisión desacoplada |
|---|---|---|---|
| Consistencia principal | Local por módulo/transacción | Local más coordinación durable | Core como registro; proyecciones asíncronas |
| Esperas externas | Worker durable para excepciones | Parte central del workflow | Orquestador junto a adaptadores |
| Complejidad operacional | Menor | Mayor | Depende de contratos/legacy |
| Desacoplamiento | Contratos dentro del backend | Eventos y APIs | Frontera del core y decisión |
| Riesgo característico | Bloqueo por dependencia compartida | Duplicados/orden/versiones | Desfase y semánticas incompatibles |
| Evidencia antes de adoptar | Latencia y aislamiento de módulos | Replay, idempotencia y estados | Conciliación y equivalencia semántica |

Las tres pueden usar servicios contratados de identidad, datos o scoring. SaaS/componente comprado es una decisión de abastecimiento, distinta del estilo arquitectónico. Ninguna variante se recomienda sin medir carga, capacidad de operación, dependencia y costo total.

## Fronteras de confianza y acceso

Zona pública: canal y API expuesta. Zona restringida: expediente, fuentes e identidad. Zona de decisión: señales minimizadas y modelos autorizados. Zona de efectos: formalización, core/pagos y controles de autorización. Zona analítica: vistas con granularidad y acceso adecuados. Revisores acceden por tarea y finalidad; desarrolladores no reciben automáticamente medios biométricos o expedientes.

Un identificador pseudónimo no hace anónimos los datos si existe una tabla de enlace. Cifrado, gestión de llaves, segregación de funciones, límites de salida y registro de acceso deben acompañar el diseño; no están implementados por dibujar un candado.
