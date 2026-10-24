# Legal Tech colombiano

Línea de investigación para asistentes jurídicos con evidencia verificable. **Estado M0: doce diseños, arquitectura y especificaciones; no hay RAG desplegado, agentes ejecutándose ni skills instaladas.**

## Proyectos

| Proyecto | Pregunta |
|---|---|
| [RAG normativo temporal](projects/01-rag-normativo-temporal) | ¿Qué disposición era aplicable a una fecha y territorio determinados? |
| [Jurisprudencia y precedente](projects/02-jurisprudencia-y-precedente) | ¿Qué decisiones apoyan o contradicen una tesis y por qué son comparables? |
| [Validador de citas jurídicas](projects/03-validador-de-citas) | ¿Existe la referencia y respalda exactamente la afirmación? |
| [RAG de expedientes privados](projects/04-rag-expedientes-privados) | ¿Qué hechos están documentados y qué evidencia falta en este expediente? |
| [Revisión contractual con playbooks](projects/05-contratos-y-clausulas) | ¿Qué cláusulas difieren del playbook aprobado y cuál es su exposición? |
| [Asistente de acceso a la justicia](projects/06-tutelas-y-peticiones) | ¿Cómo organizar hechos y soportes para un borrador revisable? |
| [Radar de cumplimiento colombiano](projects/07-cumplimiento-regulatorio) | ¿Qué cambios normativos podrían afectar una obligación de la entidad? |
| [Contratación pública y alertas documentales](projects/08-contratacion-publica) | ¿Qué inconsistencias entre pliego, adendas, oferta y contrato requieren revisión? |
| [Laboral y seguridad social](projects/09-laboral-y-seguridad-social) | ¿Qué régimen y evidencia deben examinarse antes de responder? |
| [Tributario nacional y territorial](projects/10-tributario-territorial) | ¿Qué fuente aplica al impuesto, periodo y municipio de la consulta? |
| [Términos procesales asistidos](projects/11-terminos-y-actuaciones) | ¿Qué datos y reglas se requieren para construir un calendario revisable? |
| [Clínica jurídica adversarial](projects/12-clinica-juridica-adversarial) | ¿Resiste la respuesta contraargumentos, excepciones y fuentes contradictorias? |

## Infraestructura compartida

- [Arquitecturas y flujo de agentes](docs/ARCHITECTURE.md).
- [Contratos de documentos, consultas y respuestas](docs/CONTRACTS.md).
- [Filtros y validación adversarial](docs/VALIDATION.md).
- [Especificaciones de skills](docs/SKILL_BLUEPRINTS.md).
- [Fuentes y límites de la revisión](docs/SOURCES.md).

## Orden de construcción

1. Validador de citas y contrato de evidencia: impiden que el generador entregue referencias sin resolver.
2. RAG normativo temporal: piloto pequeño con artículos y versiones revisados por un abogado.
3. Jurisprudencia: comparabilidad y contraargumentos, sin convertir el ranking en autoridad jurídica.
4. Expedientes privados: solo después de verificar aislamiento, permisos y rutas de procesamiento.
5. Especialidades y clínica adversarial: evaluar cada una con casos propios.

La fecha del caso y la fecha de consulta son campos distintos. Una respuesta histórica puede requerir fuentes anteriores que hoy estén derogadas. La ausencia de evidencia produce abstención o una solicitud de datos, nunca una referencia inventada.
