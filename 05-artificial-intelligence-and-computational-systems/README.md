# Artificial Intelligence & Computational Systems

Investigación aplicada en sistemas inteligentes, ingeniería de datos, aprendizaje automático, IA agéntica, modelos fundacionales, inferencia causal y confiabilidad computacional. El área construye **infraestructura y métodos reutilizables**, no duplica los problemas económicos, de riesgo o inversión de los dominios 01–04.

## Ocho pilares

- [Data Engineering & Platforms](data-engineering/) — MVP ejecutable, librerías compartidas y ocho plataformas de diseño
- [Machine Learning Engineering](02-machine-learning-engineering/) — 2 prototipos algorítmicos iniciales
- [Deep Learning & Foundation Models](03-deep-learning-and-foundation-models/) — 2 prototipos algorítmicos iniciales
- [Agentic AI & Multi-Agent Systems](04-agentic-ai-and-multi-agent-systems/) — 2 prototipos algorítmicos iniciales
- [Causal AI & Decision Intelligence](05-causal-ai-and-decision-intelligence/) — 2 prototipos algorítmicos iniciales
- [Knowledge Engineering & RAG](06-knowledge-engineering-and-rag/) — 2 prototipos algorítmicos iniciales
- [Intelligent Automation & Process Mining](07-intelligent-automation-and-process-mining/) — 2 prototipos algorítmicos iniciales
- [AI Reliability, Security & Governance](08-ai-reliability-security-and-governance/) — 2 prototipos algorítmicos iniciales

**Inventario:** 1 plataforma de datos con código ejecutable y utilidades probadas por CI; 8 iniciativas documentales de Data Engineering; **14 prototipos algorítmicos iniciales** en los otros siete pilares. No contar diseños como productos terminados.

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

La novedad científica exige revisión de literatura. Los 14 prototipos tienen código y tests, pero no equivalen a sistemas completos ni validados.

## Reproducción

```bash
python 05-artificial-intelligence-and-computational-systems/scripts/test_projects.py
```

[Estado y límites de implementación](IMPLEMENTATION_STATUS.md). Verificar resultados de CI antes de afirmar validación.
