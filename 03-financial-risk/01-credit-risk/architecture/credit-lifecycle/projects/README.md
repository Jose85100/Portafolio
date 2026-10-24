# Programa de proyectos del ciclo de crédito

Diez carpetas con responsabilidad propia, treinta ideas falsables, cuarenta escenarios adversariales propuestos y un contrato sintético por proyecto. **Todos los proyectos nuevos están en S1: formulación; no hay nuevos prototipos, benchmarks o pentests ejecutados.** Las implementaciones existentes enlazadas conservan su alcance y madurez.

Cada carpeta tiene README.md, EXPERIMENTS.md, SECURITY_REVIEW.md y contracts/example.json. El contrato es un ejemplo de interfaz, no un schema o servicio implementado. [Registro estructurado](projects.json), [ruta de desarrollo](ROADMAP.md), [modelo de amenazas](THREAT_MODEL.md) y [ocho capas defensivas adicionales](../defense-layers/README.md).

| Carpeta/proyecto | Pregunta propia | Prioridad | Ideas |
|---|---|---|---|
| [01-geo-device-context](01-geo-device-context/README.md) | ¿Cuándo una discrepancia de ubicación añade información verificable y cuándo solo refleja la imprecisión de la red? | P1 | GEO-01, GEO-02, GEO-03 |
| [02-provider-orchestration](02-provider-orchestration/README.md) | ¿Qué verificación conviene consultar a continuación cuando hay costo, latencia, fallos compartidos y evidencia incompleta? | P1 | PROV-01, PROV-02, PROV-03 |
| [03-credit-offer-policy](03-credit-offer-policy/README.md) | ¿Cómo elegir monto, plazo y condiciones entre ofertas admisibles considerando flujo de pago, incertidumbre y exposición concurrente? | P2 | OFFER-01, OFFER-02, OFFER-03 |
| [04-durable-origination-workflow](04-durable-origination-workflow/README.md) | ¿Cómo conservar un estado de solicitud correcto ante callbacks duplicados, evidencia tardía, vencimientos y decisiones humanas? | P1 | WF-01, WF-02, WF-03 |
| [05-disbursement-reconciliation](05-disbursement-reconciliation/README.md) | ¿Cómo evitar doble desembolso y reconstruir el estado correcto cuando la respuesta del riel es incierta? | P1 | PAY-01, PAY-02, PAY-03 |
| [06-servicing-ledger-quality](06-servicing-ledger-quality/README.md) | ¿Cuánta mora aparente puede explicar una discrepancia de calendario, imputación o fecha efectiva antes que un deterioro crediticio? | P2 | SERV-01, SERV-02, SERV-03 |
| [07-collections-treatment-design](07-collections-treatment-design/README.md) | ¿Qué acción admisible aporta recuperación incremental sin confundir facilidad de contacto con eficacia causal? | P3 | COLL-01, COLL-02, COLL-03 |
| [08-risk-data-observability](08-risk-data-observability/README.md) | ¿Cómo distinguir deterioro de riesgo de cambios de fuente, cobertura, maduración de etiquetas o errores del pipeline? | P2 | OBS-01, OBS-02, OBS-03 |
| [09-purpose-bound-signal-governance](09-purpose-bound-signal-governance/README.md) | ¿Cómo impedir que una señal disponible para seguridad se use automáticamente en otra decisión sin habilitación y evaluación? | P1 | PUR-01, PUR-02, PUR-03 |
| [10-formalization-collateral](10-formalization-collateral/README.md) | ¿Cómo demostrar que la aceptación, el instrumento, la garantía y el desembolso corresponden a la misma oferta vigente? | P2 | FORM-01, FORM-02, FORM-03 |

## Una carpeta tiene que poseer un problema

Señales geográficas no posee identidad civil. Proveedores posee consultas y cobertura; el motor de crédito posee ofertas, no efectos de pago. Workflow posee estados de solicitud; desembolso posee intención/confirmación; LMS conserva la obligación. Cobranza propone acciones admisibles sobre saldo correcto. Observabilidad distingue cambio de datos/modelo/outcome. Finalidad gobierna usos de señales. Formalización mantiene coherencia entre oferta, aceptación e instrumento.

Las capas defensivas atraviesan esos proyectos y no duplican el modelo base. La evaluación adversarial busca un fallo concreto, incluye el contraste legítimo y conserva el efecto posterior. Contar más reglas o más proveedores no prueba una mejora.

## Ideas, escenarios y estudios: unidades distintas

- **30 ideas de proyecto:** hipótesis/comparador/estimando y criterio de refutación en EXPERIMENTS.md.
- **40 escenarios adversariales:** supuestos atacables, control y fixture seguro en SECURITY_REVIEW.md; no hallazgos confirmados.
- **16 estudios transversales:** investigación de las ocho capas adicionales, conectada con esas ideas; no se suman como experimentos ya ejecutados ni se presume independencia temática.

## Convención de evidencia futura

S1 requiere formulación coherente; S2 exige datos/generador versionados, baseline ejecutable, checks/invariantes relevantes y salidas reproducibles. S3 requiere validación fuera de muestra y robustez conforme al problema; la revisión del autor no basta como aprobación independiente. Los notebooks futuros incluirán fórmulas, supuestos, gráficos, resultados negativos y referencias, sin padding para aumentar extensión.

La taxonomía S0–S4 sigue la convención de investigación del portafolio; consultar los estándares del componente que se reutilice. Los ejemplos y estudios nuevos se restringen a laboratorio sintético hasta autorización institucional explícita para otro entorno.
