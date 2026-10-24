# Capas adversariales: identidad, evidencia y efectos

Modelo de amenazas para estudiar la vulneración de supuestos del ciclo de crédito. «Contrainteligencia» se usa aquí como inteligencia de fraude y revisión crítica de fuentes/patrones, con alcance y datos habilitados. «Contraingeniería» se usa como resistencia a sondeo, manipulación de entradas, abuso de interfaces y rutas de control. Las [ocho capas adicionales](../defense-layers/README.md) convierten esos estudios en responsabilidades explícitas.

**Estado:** cuarenta escenarios de escritorio y dieciséis estudios transversales propuestos, sin pruebas contra bancos/proveedores y sin vulnerabilidades reales confirmadas. Los fixtures futuros usan datos y documentos totalmente ficticios, marcados como no válidos, y ambientes autorizados.

## Ejemplo 1: teléfono preparado con identidad reclamada distinta

El actor controla un teléfono de laboratorio y presenta una identidad reclamada. La respuesta de una verificación de posesión es favorable. El riesgo es que el sistema transforme ese hecho en identidad civil, voluntad y autorización del crédito sin evidencia adicional.

| Hecho | Qué evidencia podría aportar | Qué queda por evaluar |
|---|---|---|
| Control actual del número | Verificación de posesión/acceso al canal | Vínculo de ese controlador con la persona reclamada |
| Titularidad nominal reportada | Fuente telco habilitada y alcance del atributo | Actualidad, calidad, disponibilidad y relación real de uso |
| Documento aportado | Campos y validación específica de evidencia | Autenticidad, sujeto y vigencia |
| Vínculo sujeto/evidencia | Proceso de comprobación de identidad con alcance explícito | Riesgo de sustitución, engaño y errores |
| Intención/voluntad | Contexto y confirmación apropiada de acción | Coerción, ingeniería social y destino de fondos |
| Autorización de crédito/pago | Política, autoridad y condiciones vigentes | No se deduce automáticamente de los hechos anteriores |

Control propuesto: tipos separados y binding entre sujeto, caso, sesión, evidencia y efecto. Un `phone_possession_verified=true` no asigna `identity_link_verified=true`. Una línea legítimamente compartida es un contraste necesario: no se propone rechazar a toda persona cuyo número tenga otro titular nominal.

```json
{
  "case_id": "synthetic-identity-chain-001",
  "claimed_subject_id": "synthetic-person-A",
  "phone_possession_verified": true,
  "subscriber_relation_status": "unknown",
  "document_authenticity_status": "inconclusive",
  "subject_evidence_binding": "unverified",
  "transaction_intent_status": "not_established",
  "decision_state": "evidence_pending"
}
```

Es un caso propuesto, no ejecución ni procedimiento de activación de una línea ajena. Se conecta con PROV-A1/PROV-A4, GEO-A3, WF-A3 y HUMAN-RECOVERY. El resultado esperado es preservar evidencia pendiente y una ruta alternativa apropiada, sin acusación automática ni aprobación por canal controlado.

## Ejemplo 2: foto de cédula modificada o reutilizada

Una imagen puede producir OCR coherente y conservar su hash después de cargarse, mientras la autenticidad del documento o su vínculo con la persona siguen sin comprobarse. Un documento auténtico de un sujeto diferente también puede ser evidencia incorrecta para el caso.

Control propuesto: separar extracción de campos, autenticidad de fuente/evidencia, vínculo con persona, integridad de captura y coherencia de oferta/formalización. Consultar fuentes corroborantes solo con habilitación y cobertura verificadas; la ausencia de cobertura es un estado inconcluso. No afirmar autenticidad porque el archivo tiene buen OCR o porque no cambió después de subirse.

Fixture seguro: documento inventado con marca visible NO VÁLIDO, identificadores ficticios y variantes de consistencia de campo/origen/sujeto. No se modifica una cédula real ni se construye una receta para evadir verificación. FORM-A1/FORM-A2 y DOCUMENT-LINK evalúan si cada capa conserva su alcance antes de marcar el expediente como listo.

## Base técnica y lo que aporta el programa

NIST SP 800-63A-4 distingue resolución de identidad, validación de evidencia/atributos y verificación de su vínculo con la persona; su §3.14 trata inyección y medios manipulados. SP 800-63B-4 separa autenticación y plantea indicadores como cambios de SIM al considerar ciertos canales. FinCEN FIN-2024-Alert004 documenta medios sintéticos y documentos alterados en fraude financiero. Son referencias técnicas/de amenaza, no acreditación de estos controles ni obligación colombiana inferida.

- [NIST 800-63A-4](https://pages.nist.gov/800-63-4/sp800-63a.html)
- [NIST 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [FinCEN FIN-2024-Alert004](https://www.fincen.gov/system/files/shared/FinCEN-Alert-DeepFakes-Alert508FINAL.pdf)

La distinción de tipos, los ejemplos y los estudios son diseño propio. Los artículos y documentación comercial del [registro de fuentes](../sources.json) mantienen su alcance; no se afirma que un proveedor particular sea vulnerable a estos casos.

## Encadenamiento a estudiar

Un caso puede combinar canal bajo control, documento aparente, fuente sin cobertura, revisión bajo presión y cambio de destino. La evaluación de sistema comprueba si una ruta alternativa omite un control necesario, no solo si un detector aislado reconoce un archivo. La misma prueba incluye un caso legítimo con cambios de teléfono/documento y falta de cobertura para medir daño por exceso de bloqueo.

## Protocolo de evaluación y evidencia futura

1. Definir activo, capacidad del actor, ambiente autorizado y reglas de parada. Separar manipulación de entrada, fuente comprometida, error accidental y abuso de rol.
2. Construir baseline y fixtures sintéticos versionados; reservar familias no utilizadas para ajustar controles. Los escenarios del registro no son resultados.
3. Registrar estado/versión de cada control, transiciones, actor y efecto simulado. Un control no ejecutado no cuenta como pase.
4. Medir aceptación indebida de escenario, falsos bloqueos de legítimos, cobertura, abstención, revisión, demora y costo sobre el mismo universo.
5. Conservar resultado negativo, causa y riesgo residual. Repetir tras una corrección con controles vecinos; la mejora no se mide solo en el caso que motivó el parche.

Un fallo crítico de autoridad, vínculo de evidencia o doble efecto bloquea la promoción del prototipo. No se fija aquí una tasa de ataque aceptable universal ni se afirma invulnerabilidad por cero fallos en una muestra finita. Sin embargo, el laboratorio debe demostrar que captura los contraejemplos que motivaron su diseño.

## Límites del estudio

No hay procedimientos para falsificar identidades, activar líneas ajenas, generar documentos engañosos utilizables, extraer modelos de terceros o probar evasión en servicios reales. La finalidad es estudiar supuestos y respuestas defensivas con fixtures autorizados. La revisión de fuentes y de contratos no acredita controles desplegados ni reemplaza evaluación independiente.
