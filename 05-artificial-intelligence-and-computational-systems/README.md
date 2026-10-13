# Artificial Intelligence & Computational Systems

Investigación aplicada en sistemas inteligentes, ingeniería de datos, aprendizaje automático, IA agéntica, modelos fundacionales, inferencia causal y confiabilidad computacional. El área construye **infraestructura y métodos reutilizables**, no duplica los problemas económicos, de riesgo o inversión de los dominios 01–04.

## Ocho pilares

- [Data Engineering & Platforms](data-engineering/) — MVP ejecutable, librerías compartidas y ocho plataformas de diseño
- [Machine Learning Engineering](02-machine-learning-engineering/) — 2 propuestas de investigación
- [Deep Learning & Foundation Models](03-deep-learning-and-foundation-models/) — 2 propuestas de investigación
- [Agentic AI & Multi-Agent Systems](04-agentic-ai-and-multi-agent-systems/) — 2 propuestas de investigación
- [Causal AI & Decision Intelligence](05-causal-ai-and-decision-intelligence/) — 2 propuestas de investigación
- [Knowledge Engineering & RAG](06-knowledge-engineering-and-rag/) — 2 propuestas de investigación
- [Intelligent Automation & Process Mining](07-intelligent-automation-and-process-mining/) — 2 propuestas de investigación
- [AI Reliability, Security & Governance](08-ai-reliability-security-and-governance/) — 2 propuestas de investigación

**Inventario:** 1 plataforma de datos con código ejecutable y utilidades probadas por CI; 8 iniciativas documentales de Data Engineering; **14 nuevas propuestas técnicas** en los otros siete pilares. No contar diseños como productos terminados.

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

La novedad científica debe establecerse mediante revisión de literatura; las nuevas carpetas no contienen todavía implementaciones.

## Advanced AI Systems Engineering — 10 proyectos adicionales

Se añade [un noveno pilar](09-advanced-ai-systems-engineering/) con diez proyectos de ingeniería avanzada, bases compartidas y un kernel C++20 inicial de benchmarks. Se preservan los ocho pilares y el código existente. No confundir las diez especificaciones con diez sistemas productivos.

## Proyectos con implementación ejecutable (librería + pruebas + notebook)

Tres proyectos se construyeron como librerías probadas, con notebooks extensos que validan cada método contra una verdad conocida y no necesitan red ni claves de API:

| Proyecto | Pilar | Qué demuestra |
|---|---|---|
| [Recuperación para RAG](06-knowledge-engineering-and-rag/rag-retrieval-evaluation/) | Knowledge Engineering & RAG | Qué decisiones de un RAG importan de verdad, con corpus real, pruebas pareadas y potencia |
| [Confiabilidad de agentes](04-agentic-ai-and-multi-agent-systems/agent-runtime-reliability/) | Agentic AI | Falla metaestable por reintentos, presupuesto de reintentos, cortacircuitos, idempotencia y sagas |
| [Evaluación de LLM y jueces](08-ai-reliability-security-and-governance/llm-evaluation-judge-reliability/) | AI Reliability | Intervalos, PPI, sesgos de jueces, acuerdo, comparaciones múltiples y compuertas secuenciales |

Según la [matriz de madurez](../PROJECT_MATURITY.md) están en **M2 (prototipo verificado)**: pruebas automáticas, resultados reproducibles y límites explícitos; no tienen evaluación independiente ni datos operativos.


## AI Orchestration Engineering

- [Seven AI orchestration projects](10-ai-orchestration-engineering/): distributed workflow scheduling, multi-agent coordination, routing, events, memory, recovery and governance.

## AI Literacy and Digital Twins

- [Five AI Literacy projects](11-ai-literacy-and-human-ai-competence/): competency assessment, evidence, task specifications, human-AI decisions and responsible use.
- [Digital Twins & Intelligent Simulation](12-digital-twins-and-intelligent-simulation/): 27 research project specifications across banking, macroeconomics, innovation and public policy.

## Enterprise AI Backend Engineering

- [Five enterprise AI backend projects](13-enterprise-ai-backend-engineering/): Kotlin, Rust, REST, identity, distributed execution, RAG and AI-assisted software delivery.
