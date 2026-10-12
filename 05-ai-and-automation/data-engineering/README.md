# Ingeniería de datos

Esta línea reúne cinco ejercicios de ingeniería orientados a problemas que aparecen al trabajar con datos económicos y financieros: cortes de cartera, revisiones de series, calidad, disponibilidad temporal y ejecución repetible de pipelines.

## Proyectos

| Proyecto | Problema | Implementación |
|---|---|---|
| [Risk Data Platform](01-risk-data-platform/) | Reconstruir una cartera a una fecha sin duplicar registros | Python, SQL, C++17 |
| [Macro Data Lakehouse](02-macro-data-lakehouse/) | Consultar datos macro según lo conocido en cada momento | Python/SQLite, SQL PostgreSQL |
| [Data Quality & Lineage](03-data-quality-lineage/) | Identificar fallos y conservar evidencia de los archivos evaluados | Python, SQL |
| [Quant Research Data Factory](04-quant-research-data-factory/) | Preparar características y etiquetas sin contaminación temporal | Python, SQL, C++17 |
| [Workflow Orchestrator](05-workflow-orchestrator/) | Ejecutar dependencias con reintentos y checkpoints | Python, SQL |

## Cómo se han diseñado

Los módulos Python son las implementaciones de referencia. Los archivos SQL describen un modelo relacional en PostgreSQL, pero no implican que exista una base desplegada. Los dos programas C++17 son ejecutables separados para tareas concretas; no están conectados al código Python por bindings.

Cada proyecto tiene pruebas unitarias. Cuatro incluyen también un documento de arquitectura con diagramas Mermaid; el documento de arquitectura del lakehouse sigue pendiente. Prefiero mantener esta distinción antes que presentar una plataforma integrada que todavía no existe.

## Ejecutar las pruebas

```bash
for project in 05-ai-and-automation/data-engineering/0[1-5]-*; do
  python3 -m unittest discover -s "$project/tests" -p 'test_*.py' -v
done
```

El workflow [Data Engineering Projects](../../../.github/workflows/data-engineering.yml) incluye pruebas Python y compilación de C++. La ejecución completa del CI aún debe confirmarse.

## Próximo trabajo

Integración entre componentes, pruebas con PostgreSQL, mediciones de rendimiento, migraciones de esquema, observabilidad y manejo seguro de credenciales. Los ejemplos no contienen datos de clientes.
