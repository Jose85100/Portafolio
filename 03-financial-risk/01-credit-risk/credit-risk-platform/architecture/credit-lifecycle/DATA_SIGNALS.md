# Información que puede observar, solicitar o derivar un banco

Este catálogo describe **posibilidades técnicas y propuestas de uso**, no acceso universal. Ver [35 señales estructuradas](signal_catalog.csv) y [marco colombiano](COLOMBIA_DATA_USE.md). Antes de captar una señal se define el producto, finalidad, fuente y habilitación; después se prueba su utilidad. No se recolectan todas por defecto.

## Tres preguntas diferentes

1. **¿Está disponible?** IP en conexión; posición por API y permiso; ingresos mediante cliente/fuente autorizada; buró con acceso contractual. Cada mecanismo tiene restricciones.
2. **¿Puede tratarse para esta finalidad?** Determinar régimen y habilitación, roles, comunicación a proveedores, conservación y derechos. El permiso del sistema operativo no responde esa pregunta completa.
3. **¿Sirve para esta decisión?** Validar aporte incremental, sesgo, estabilidad, costos y ruta si falta. Una variable útil para fraude no pasa automáticamente al modelo de capacidad de pago.

## Captación técnica: diferencias esenciales

| Señal | Cómo se obtiene | Qué permite inferir razonablemente | Qué no demuestra |
|---|---|---|---|
| IP pública | Conexión al servidor o cadena de proxies de confianza | Punto de salida y contexto de red | Persona única, domicilio o coordenada GPS |
| ASN/operador | Enriquecimiento de IP | Organización/red anunciada o clasificación estimada | Propietario de la cuenta o dispositivo |
| GeoIP | Base o API de enriquecimiento | Área aproximada, con radio/calidad disponibles | Dirección residencial exacta |
| Ubicación de dispositivo | API de localización de navegador/app con permiso | Estimación en un momento con precisión declarada | Verdad física infalible; la API no garantiza usar GPS |
| Huella/ID de dispositivo | SDK, ID de instalación y atributos disponibles | Continuidad probable o cambio de entorno | IMEI universal ni identificación civil permanente |
| Comportamiento | Eventos de UI y sesión definidos | Cambios, automatización o señales para investigar | Engaño, coerción o capacidad de pago por sí solos |
| Telco | Producto de operador/proveedor contratado | Atributos de número/cambio de SIM si hay cobertura | Acceso a SMS, llamadas privadas o ubicación telco por defecto |
| Fuentes financieras | Relación bancaria propia o conexión habilitada | Flujos disponibles del usuario/cuenta conectada | Información de todas las entidades sin acceso específico |

Fuentes técnicas: W3C [S:w3c], Android [S:android], MaxMind [S:maxmind; S:maxmind-vpn], Fingerprint [S:fingerprint] y Telesign [S:telesign]. No se adoptan cifras comerciales de precisión como validación local.

## IP: diseño de captura y falsas asociaciones

La IP observada puede ser la del balanceador/proxy. La aplicación debe aceptar encabezados de dirección original solo de infraestructura confiable; un `X-Forwarded-For` enviado por cualquier cliente no se convierte en evidencia autenticada. Registrar el punto de observación y la cadena de confianza necesaria, no copiar encabezados arbitrarios a un score.

NAT/CGNAT, oficinas, hogares, comercios y redes móviles agrupan personas; las IP también cambian. Diseñar conteos de solicitudes por IP junto con canal, dispositivo, tiempo y cobertura. Deduplicar reintentos. Un conteo alto genera contexto de investigación, no una lista automática de culpables.

Una VPN/Tor/proxy es una señal contextual con usos legítimos. La geolocalización de la salida del túnel puede corresponder al intermediario [S:maxmind-vpn]. Comparar país/región declarados solo dentro de la precisión de la fuente. Guardar versión/fecha de la base para replay; actualizar una base después no cambia lo conocido en la decisión histórica.

## Geolocalización: usar incertidumbre y tiempo

Guardar método, coordenadas solo con la precisión necesaria, `accuracy_m`, momento de medición, disponibilidad y resultado de permiso. En GeoIP el radio puede estar en kilómetros y depender del producto; convertir unidades explícitamente. La ausencia de radio no significa radio cero.

Una regla de «viaje imposible» que trate centros de áreas como posiciones exactas puede generar alertas falsas. Como heurística propia, con distancia geodésica d, radios r1/r2 y lapso positivo dt:

\[
d_{min}=\max(0,d-r_1-r_2),\qquad v_{min}=d_{min}/\Delta t.
\]

Solo es un límite geométrico bajo la interpretación de esos radios como regiones válidas; los radios de proveedor no son cotas físicas garantizadas. Si falta tiempo/radio, si cambió el método o si el dato está obsoleto, la salida será inconclusa. No mezclar una posición precisa y una ciudad GeoIP como si tuvieran igual certidumbre. La lógica propuesta debe evaluarse con viajes legítimos y cambios de red.

La ubicación precisa puede revelar patrones delicados y crear proxies de exclusión. Propuesta de arquitectura: captación puntual justificada, minimización espacial, retención diferenciada y separación de variables antifraude de underwriting. No se propone rastreo continuo ni localización de deudores para presionarlos.

## Dispositivo y comportamiento

Usar un identificador de instalación con alcance definido y distinguir «ID cambió» de «persona cambió». Los SDK pueden identificar emuladores, manipulación o patrones bajo su cobertura, pero su ausencia/timeout es un estado distinto. Android restringe identificadores no reiniciables como IMEI y serial en circunstancias ordinarias [S:android]. El diseño no depende de MAC/IMEI ni de un identificador publicitario persistente.

Capturar tiempos, número de reintentos o agregados de navegación cuando estén justificados. Excluir contraseñas, PIN, OTP y contenido de campos secretos de telemetría. No construir un keylogger para riesgo de crédito. La accesibilidad, asistencia de un familiar y uso de teclado alternativo necesitan evaluación de falsos positivos.

## Fuentes financieras y expediente

Ingresos declarados, verificados, estimados y faltantes tienen estados diferentes. Un depósito no es automáticamente salario: conciliar préstamos, transferencias propias, devoluciones, titular y período. Un buró aporta la información reportada que cubre su contrato; no entrega por defecto el extracto de cada cuenta. Listas y KYC/KYB tampoco habilitan consultar cualquier base gubernamental.

Firma y pagaré se incorporan al expediente con su versión y evidencias. Un resultado técnico favorable no reemplaza revisión jurídica de formalización. Tras desembolso, ledger/pagos/calendario son fuentes primarias para saldo y DPD; una alerta de analítica no sobrescribe contabilidad.

## Datos excluidos por defecto en esta propuesta

Agenda de contactos, galería completa, micrófono continuo, SMS privados, credenciales bancarias, contraseñas, navegación fuera del canal e inferencias de salud/religión/política. No se afirma que toda categoría tenga idéntica prohibición legal: se excluyen por falta de necesidad demostrada en este diseño. Una extensión exige análisis específico; el SDK no es una autorización genérica.

## Contrato de señal propuesto

```json
{
  "case_id": "synthetic-case-001",
  "session_id": "synthetic-session-001",
  "signal_name": "device_location",
  "status": "not_collected",
  "method": "device_geolocation_api",
  "value": null,
  "accuracy_m": null,
  "event_time": null,
  "available_time": "2026-10-23T20:00:00Z",
  "purpose_id": "fraud_context_v1",
  "authorization_ref": null,
  "platform_permission": "not_requested",
  "source_version": "design-example",
  "retention_policy_id": "institution-to-define",
  "permitted_decision_uses": ["fraud_context"]
}
```

Contrato de diseño, no implementado como API. Estados diferenciados: `not_collected`, `permission_denied`, `unavailable`, `stale`, `observed`, `estimated`, `verified`, `inconclusive`. Las transiciones y semántica se definen por señal; «verified» nunca significa que toda la persona sea legítima. La política no puede imputar un permiso denegado como GPS cero ni fraude confirmado.

En producción, separar vault de identificadores/medios, store de señales minimizadas, snapshot de decisión, ledger de efectos y vistas analíticas. Los registros contienen referencias protegidas y acceso por rol/finalidad. Retención y borrado requieren reglas institucionales por categoría y obligaciones aplicables; no se inventa un número universal de días.
