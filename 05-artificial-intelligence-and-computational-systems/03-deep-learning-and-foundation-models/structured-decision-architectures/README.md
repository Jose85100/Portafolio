# Arquitecturas de decisiones estructuradas

Dos diseños de sistemas con contratos y experimentos locales. **Estado: diseño de integración comercial y prototipo sintético de componentes**. No implementan la arquitectura interna de Jev ni de ScaleDown y no se ejecutó ninguna API comercial. CDM aquí significa Constrained Decoding Models de ScaleDown, no modelos de difusión.

| Arquitectura | Pregunta | Notebook | Reutilización |
|---|---|---|---|
| [Decisión tipada](01-typed-decision-cascade/) | ¿Cuándo aceptar una clasificación y cuándo derivar? | [Calibración, riesgo y costo](01-typed-decision-cascade/notebook.ipynb) | Cascadas, jueces y gobernanza existentes |
| [Documento con evidencia](02-evidence-preserving-document-pipeline/) | ¿Cómo conservar la fuente hasta la decisión? | [Spans, conciliación y fallos](02-evidence-preserving-document-pipeline/notebook.ipynb) | Contratos ELT, RAG y checkpoints existentes |

## Organización y alcance

`src/contracts.py` contiene el contrato neutral, selección de umbral con cota simultánea, costo esperado por acción y evidencia con hash/offset. `tests/` contrasta acciones con enumeración y evidencia con alteraciones. Cada arquitectura contiene su propio flujo, capas, fórmulas, límites y notebook. El plan de experimentos se regenera mediante `scripts/deepen_20261023_notebooks.py` desde la raíz.

No se crea un undécimo pilar: los modelos de decisión se estudian en Foundation Models, la orquestación sigue en el pilar 10 y los problemas crediticios en el dominio 03. Las API futuras solo producirán señales; el sistema consumidor deberá verificar semántica, calibración local y costo.

## Reproducción sin credenciales

```bash
python -m pip install -r 05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/requirements.txt
cd 05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures
python -m unittest discover -s tests -v
```

Desde la raíz: `python scripts/deepen_20261023_notebooks.py`; luego `python scripts/execute_research_depth.py --mode kernel` ejecuta los siete notebooks de esta ampliación. `--mode ipython` usa un proceso fresco por notebook cuando el entorno restringe sockets. Ambos guardan outputs, figuras incrustadas y evidencia; no realizan llamadas de red.

## Fuentes primarias, consultadas el 23 de octubre de 2026

- [TypeSafe: introducción de Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev): estado no estructurado y decisiones tipadas probabilísticas. Las cifras comerciales de rendimiento no se usan como medición de nuestros sistemas.
- [TypeSafe: índice de documentación](https://docs.typesafe.ai/llms.txt): Choice, Score, Noul y recetas de decisión/extracción. Las capacidades/versiones deberán verificarse otra vez antes de conectar producción.
- [ScaleDown: introducción](https://docs.scaledown.ai/introduction): modelos especializados, clasificación y extracción.
- [ScaleDown: índice](https://docs.scaledown.ai/llms.txt): endpoints separados para Classify, Extract y Decisions. Compatibilidad de formato no acredita equivalencia semántica.
- [LangChain: integración ScaleDown](https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents): clasificación, extracción con posición en fuente y gestión de contexto.

Las fuentes describen interfaces y productos. Las políticas, costos, pruebas y fórmulas de los notebooks son diseños propios reproducibles, no revelaciones del entrenamiento propietario.
