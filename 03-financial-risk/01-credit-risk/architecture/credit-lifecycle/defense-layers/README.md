# Ocho capas defensivas adicionales del ciclo de crédito

Capas lógicas de protección y estudio: se superponen a las 15 responsabilidades del ciclo, sin reemplazar los motores base ni exigir ocho servicios nuevos. Cada carpeta tiene objetivo, dueño propuesto, controles, dos estudios y riesgo residual. **Estado S1; las 16 investigaciones no se ejecutaron.**

| Capa | Objetivo | Etapas | Estudios |
|---|---|---|---|
| [Integridad, procedencia y vínculo de evidencia](01-evidence-integrity/README.md) | Evitar que un archivo, teléfono, rostro o respuesta de proveedor favorable se use para afirmar algo que no verificó. | Captación, KYC, Formalización, Antes del desembolso | PHONE-LINK, DOCUMENT-LINK |
| [Inteligencia de fraude y contexto de amenaza](02-fraud-intelligence/README.md) | Interpretar patrones de abuso y dependencias con procedencia, confianza, vigencia y alternativa benigna. | Canales, Orquestación, Investigación, Monitoreo | INTEL-PROVENANCE, INTEL-EXPIRY |
| [Evaluación adversarial y revisión de supuestos](03-adversarial-evaluation/README.md) | Buscar fallos de interacción, rutas alternativas y familias no vistas antes de liberar un cambio. | Diseño, Calibración, Validación, Sombra | ADV-CHAIN, ADV-HOLDOUT |
| [Protección frente a sondeo y contraingeniería](04-model-abuse-defense/README.md) | Reducir abuso de interfaces, inferencias indebidas y extracción de información sin sacrificar explicación fiel y derechos. | API, Motor de decisión, Explicación, Observabilidad | MODEL-PROBING, MODEL-EXPLANATION |
| [Controles humanos, recuperación e intervención interna](05-human-insider-controls/README.md) | Impedir que presión, urgencia, ingeniería social o privilegio interno sustituyan evidencia y atribución. | Soporte, Recuperación de cuenta, Analista/comité, Cambios de cuenta o términos | HUMAN-OVERRIDE, HUMAN-RECOVERY |
| [Análisis de coordinación y vínculos entre casos](06-network-coordination/README.md) | Investigar redes de solicitudes, teléfonos, dispositivos y destinos sin propagar culpabilidad entre vecinos legítimos. | Originación, Fraude, Destino de fondos, Investigación | NETWORK-BENIGN, NETWORK-DESTINATION |
| [Vigilancia continua y detección de degradación](07-continuous-assurance/README.md) | Detectar pérdida de cobertura, cambios de proveedor y controles omitidos mientras se conserva diagnóstico y rollback. | Producción futura, Monitoreo, Release, Validación | ASSURE-CANARY, ASSURE-HORIZON |
| [Respuesta, contención y aprendizaje de incidentes](08-incident-response/README.md) | Limitar impacto, preservar evidencia y corregir controles sin reescribir efectos ni convertir sospechas en labels confirmadas. | Detección, Operaciones, Pagos, Aprendizaje posterior | RESP-TIMEOUT, RESP-LABEL |

## Ubicación en la arquitectura

Las capas de integridad y finalidad actúan desde la captura. Inteligencia y coordinación interpretan señales con procedencia y alternativas benignas. Evaluación adversarial y protección de interfaces examinan decisiones y rutas de control. Controles humanos cubren soporte/excepciones. Vigilancia y respuesta conservan estado, cobertura y aprendizaje posterior.

[Cuatro vistas editables de defensa](diagrams/README.md) · [Modelo transversal de amenazas](../projects/THREAT_MODEL.md) · [Diez proyectos](../projects/README.md) · [Registro de capas y estudios](layers.json).

## Mapa de aplicación a los proyectos

| Proyecto | Capas relacionadas |
|---|---|
| [01-geo-device-context](../projects/01-geo-device-context/README.md) | [02](02-fraud-intelligence/README.md), [03](03-adversarial-evaluation/README.md), [04](04-model-abuse-defense/README.md), [06](06-network-coordination/README.md) |
| [02-provider-orchestration](../projects/02-provider-orchestration/README.md) | [01](01-evidence-integrity/README.md), [02](02-fraud-intelligence/README.md), [03](03-adversarial-evaluation/README.md), [06](06-network-coordination/README.md), [07](07-continuous-assurance/README.md) |
| [03-credit-offer-policy](../projects/03-credit-offer-policy/README.md) | [03](03-adversarial-evaluation/README.md), [04](04-model-abuse-defense/README.md) |
| [04-durable-origination-workflow](../projects/04-durable-origination-workflow/README.md) | [01](01-evidence-integrity/README.md), [03](03-adversarial-evaluation/README.md), [05](05-human-insider-controls/README.md), [08](08-incident-response/README.md) |
| [05-disbursement-reconciliation](../projects/05-disbursement-reconciliation/README.md) | [01](01-evidence-integrity/README.md), [03](03-adversarial-evaluation/README.md), [05](05-human-insider-controls/README.md), [06](06-network-coordination/README.md), [08](08-incident-response/README.md) |
| [06-servicing-ledger-quality](../projects/06-servicing-ledger-quality/README.md) | [03](03-adversarial-evaluation/README.md), [07](07-continuous-assurance/README.md) |
| [07-collections-treatment-design](../projects/07-collections-treatment-design/README.md) | [03](03-adversarial-evaluation/README.md), [05](05-human-insider-controls/README.md), [08](08-incident-response/README.md) |
| [08-risk-data-observability](../projects/08-risk-data-observability/README.md) | [02](02-fraud-intelligence/README.md), [03](03-adversarial-evaluation/README.md), [04](04-model-abuse-defense/README.md), [06](06-network-coordination/README.md), [07](07-continuous-assurance/README.md), [08](08-incident-response/README.md) |
| [09-purpose-bound-signal-governance](../projects/09-purpose-bound-signal-governance/README.md) | [02](02-fraud-intelligence/README.md), [03](03-adversarial-evaluation/README.md), [04](04-model-abuse-defense/README.md), [07](07-continuous-assurance/README.md) |
| [10-formalization-collateral](../projects/10-formalization-collateral/README.md) | [01](01-evidence-integrity/README.md), [03](03-adversarial-evaluation/README.md), [05](05-human-insider-controls/README.md) |

La relación es de estudio e integración, no de controles ya ejecutados. Una capa seleccionada tiene que observarse en un contrato y una prueba: «más seguridad» sin evidencia no es criterio de éxito.

## Dos distinciones que el diseño conserva

- **Teléfono:** control del canal, titularidad nominal, identidad verificada y voluntad de la acción son hechos diferentes. Un pase de OTP no completa por sí solo la cadena.
- **Documento:** OCR, hash, autenticidad, vínculo con sujeto y soporte de una afirmación son verificaciones distintas. La foto coherente no resuelve todas.

[Casos detallados y referencias técnicas](../projects/THREAT_MODEL.md). La inteligencia de fraude usa fuentes habilitadas; no se propone vigilancia personal ni captación indiscriminada. La protección frente a sondeo no permite inventar razones u ocultar errores que deben ser revisables.
