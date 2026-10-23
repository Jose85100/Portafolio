# Artificial Intelligence & Computational Systems

Investigación aplicada en sistemas inteligentes, ingeniería de datos, aprendizaje automático, IA agéntica, modelos fundacionales, inferencia causal y confiabilidad computacional. El área construye **infraestructura y métodos reutilizables**, no duplica los problemas económicos, de riesgo o inversión de los dominios 01–04.

## Pilares iniciales y extensiones

- [Data Engineering & Platforms](data-engineering/) — MVP ejecutable, librerías compartidas y ocho plataformas de diseño
- [Machine Learning Engineering](02-machine-learning-engineering/) — diseños y componentes con madurez diferenciada
- [Deep Learning & Foundation Models](03-deep-learning-and-foundation-models/) — diseños y componentes con madurez diferenciada
- [Agentic AI & Multi-Agent Systems](04-agentic-ai-and-multi-agent-systems/) — diseños y componentes con madurez diferenciada
- [Causal AI & Decision Intelligence](05-causal-ai-and-decision-intelligence/) — diseños y componentes con madurez diferenciada
- [Knowledge Engineering & RAG](06-knowledge-engineering-and-rag/) — diseños y componentes con madurez diferenciada
- [Intelligent Automation & Process Mining](07-intelligent-automation-and-process-mining/) — diseños y componentes con madurez diferenciada
- [AI Reliability, Security & Governance](08-ai-reliability-security-and-governance/) — diseños y componentes con madurez diferenciada

**Organización:** ocho pilares iniciales, el pilar 09 de sistemas avanzados y el pilar 10 de orquestación. Coexisten propuestas y componentes ejecutables. El [mapa de arquitectura](ARCHITECTURE.md) identifica propietarios y conexiones; el [inventario del 23 de octubre](../reviews/2026-10-23-alignment/notebooks.csv) registra notebooks sin equiparar tamaño con calidad.

## Arquitectura de datos

El código existente permanece íntegro bajo [Data Engineering](data-engineering/): `risk-data-platform`, `shared`, contratos y diseños. Los workflows CI se actualizan a la ruta nueva.

## Priorización

1. Reliability y feature-store point-in-time como cimientos transversales.
2. Evaluación de agentes con evidencia y trazabilidad.
3. Temporal Regulatory GraphRAG y auditoría de citas.
4. Conformal Risk Prediction y monitoreo probabilístico.
5. Verifiable Workflow Orchestration y AI Governance.

## Reglas de madurez

- **Diseño:** pregunta, hipótesis, especificación y riesgos.
- **Prototipo:** código, tests, baseline y datos públicos reproducibles.
- **Validado:** métricas fuera de muestra, robustez, seguridad y evaluación independiente.
- **Operacional:** observabilidad, permisos, auditoría, rollback y SLO.

La novedad científica debe establecerse mediante revisión de literatura. Los diseños conservan su estado aunque un subcomponente tenga una implementación sintética.

## Advanced AI Systems Engineering — 10 proyectos adicionales

Se añade [un noveno pilar](09-advanced-ai-systems-engineering/) con diez proyectos de ingeniería avanzada, bases compartidas y un kernel C++20 inicial de benchmarks. Se preservan los ocho pilares y el código existente. No confundir las diez especificaciones con diez sistemas productivos.

## Proyectos con implementación ejecutable (librería + pruebas + notebook)

Cinco proyectos se construyeron como librerías probadas, con notebooks extensos que validan cada método contra una verdad conocida y no necesitan red ni claves de API:

| Proyecto | Pilar | Qué demuestra |
|---|---|---|
| [Recuperación para RAG](06-knowledge-engineering-and-rag/rag-retrieval-evaluation/) | Knowledge Engineering & RAG | Qué decisiones de un RAG importan de verdad, con corpus real, pruebas pareadas y potencia |
| [Confiabilidad de agentes](04-agentic-ai-and-multi-agent-systems/agent-runtime-reliability/) | Agentic AI | Falla metaestable por reintentos, presupuesto de reintentos, cortacircuitos, idempotencia y sagas |
| [Evaluación de LLM y jueces](08-ai-reliability-security-and-governance/llm-evaluation-judge-reliability/) | AI Reliability | Intervalos, PPI, sesgos de jueces, acuerdo, comparaciones múltiples y compuertas secuenciales |
| [Contratos de datos y ELT incremental](data-engineering/data-pipeline-contracts-incremental-elt/) | Data Engineering | Contratos, evolución de esquemas, pipeline idempotente y transaccional, SCD2 y conciliación |
| [Enrutar entre modelos](03-deep-learning-and-foundation-models/model-routing-cascade-economics/) | Deep Learning & Foundation Models | Cascadas, enrutador aprendido, caché semántico, bandidos y control conforme del riesgo |

Según la [matriz de madurez](../PROJECT_MATURITY.md) están en **M2 (prototipo verificado)**: pruebas automáticas, resultados reproducibles y límites explícitos; no tienen evaluación independiente ni datos operativos.


## AI Orchestration Engineering

- [Seven AI orchestration projects](10-ai-orchestration-engineering/): distributed workflow scheduling, multi-agent coordination, routing, events, memory, recovery and governance.

## Decisiones estructuradas y revisión del 23 de octubre

- [Dos arquitecturas para decisiones tipadas y evidencia documental](03-deep-learning-and-foundation-models/structured-decision-architectures/): contratos locales, pruebas y dos notebooks extensos; integración de Jev/CDM diseñada, sin API comercial ejecutada.
- [Conformal ponderado bajo cambio de covariables](02-machine-learning-engineering/02-conformal-risk-prediction/): MVP sintético de hoy con notebook ampliado, sensibilidad de pesos y diagnóstico de intervalos infinitos.
- [Recuperación durable SQLite](10-ai-orchestration-engineering/06-fault-tolerant-ai-execution-recovery/mvp-durable-checkpoints/): componente ya existente; atomicidad local no implica exactly-once remoto.
- [Revisión semanal y estado de las PR de hoy](../reviews/2026-10-23-alignment/README.md): inventario, correcciones, evidencia ejecutada y límites de cobertura.
