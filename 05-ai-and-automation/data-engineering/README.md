# Data Engineering — Ingeniería de Datos

Línea independiente dentro de AI Architecture & Automation, con foco en plataformas analíticas y de riesgo financiero.

## Áreas

- Arquitecturas batch, microbatch y streaming; lakehouse, warehouse y data marts.
- Modelado dimensional, Data Vault, contratos de datos y evolución de esquemas.
- ELT/ETL, CDC, ingesta de APIs, bases SQL, almacenamiento de objetos.
- Orquestación con n8n, Airflow y Dagster; idempotencia, reintentos y backfills.
- Calidad de datos, observabilidad, reconciliación, linaje y manifiestos de evidencia.
- Infraestructura como código, CI/CD, seguridad, control de acceso y costos.
- Data products para econometría, IFRS 9, riesgos, nowcasting y motores quant.

## Productos propuestos

1. **Risk Data Platform**: ingesta D+1, normalización, calidad, versionamiento y publicación de datasets de riesgo.
2. **Macro Data Lakehouse**: ingesta reproducible de series públicas, calendarios de publicación, vintage data y nowcasting.
3. **Data Quality & Lineage Engine**: reglas declarativas, auditoría, alertas, linaje y reconciliación de métricas.
4. **Quant Research Data Factory**: pipelines para experimentos, datasets point-in-time, feature store y reproducibilidad.
5. **Workflow Orchestrator**: automatizaciones SQL/Python/n8n con control de fallos, reejecución segura y alertas.

## Estándar de entrega

Cada producto debe documentar arquitectura física y lógica, esquemas, contratos, SLA/SLO, pruebas, seguridad, reproducibilidad, costos, observabilidad y límites operativos.

**Estado:** cinco prototipos de referencia implementados en Python, con esquemas SQL PostgreSQL; dos incluyen ejecutables C++17. No constituyen servicios de producción.

## Relación con otros dominios

- Economía: series temporales, datos públicos y revisiones de datos.
- Riesgos: cartera, provisiones, liquidez y mercado.
- Quant: precios, factores, señales y backtesting point-in-time.
- IA: pipelines RAG, agentes y evaluación de modelos.

## Proyectos implementados (prototipos reproducibles)

1. [Risk Data Platform](01-risk-data-platform/) — snapshot D+1, validación y publicación atómica.
2. [Macro Data Lakehouse](02-macro-data-lakehouse/) — SQLite, vintages y consultas as-of.
3. [Data Quality & Lineage Engine](03-data-quality-lineage/) — reglas y evidencia SHA-256.
4. [Quant Research Data Factory](04-quant-research-data-factory/) — features y etiquetas forward con purga temporal.
5. [Workflow Orchestrator](05-workflow-orchestrator/) — DAG, reintentos y checkpoints.

Cada proyecto incluye módulo Python y pruebas unitarias. El workflow [data-engineering.yml](../../../.github/workflows/data-engineering.yml) ejecuta la batería en Python 3.11, 3.12 y 3.13. **Estado: prototipos funcionales sin validación de CI confirmada; no son sistemas productivos.**

## Distribución por lenguaje

| Proyecto | Python | SQL PostgreSQL | C++17 |
|---|---|---|---|
| Risk Data Platform | Snapshot y publicación atómica | Ledger y posición D+1 | CLI de agregación en centavos enteros |
| Macro Data Lakehouse | SQLite con vintages | Registro de publicaciones y revisiones | — |
| Data Quality & Lineage | Reglas, hash y manifiesto | Runs, resultados y grafo de linaje | — |
| Quant Research Data Factory | Features y purga temporal | Precios as-of y registro de features | CLI de momentum y etiquetas |
| Workflow Orchestrator | DAG, reintentos, checkpoints | Estado durable y leasing | — |

**Decisión de ingeniería:** Python implementa los flujos de referencia, SQL especifica almacenamiento relacional PostgreSQL y C++ acelera dos transformaciones determinísticas. Los módulos no están integrados todavía en un despliegue único: los esquemas PostgreSQL y el almacenamiento SQLite son alternativas/etapas distintas. No se simula una integración inexistente.

### Verificación

```bash
for project in 05-ai-and-automation/data-engineering/0[1-5]-*; do
  python3 -m unittest discover -s "$project/tests" -p 'test_*.py' -v
done
```

Los ejecutables C++17 se compilan y se prueban mediante el workflow de GitHub Actions. Los esquemas SQL requieren PostgreSQL 15+ para ejecutarse; no se afirma que estén desplegados. No usar archivos CSV con campos entrecomillados en los CLIs C++, pues sus lectores están deliberadamente restringidos a formatos sin comillas.

## Documentación arquitectónica

Los proyectos 01, 03, 04 y 05 incluyen `docs/ARCHITECTURE.md` con diagramas Mermaid de componentes y secuencia, invariantes, pruebas y deuda técnica. La documentación específica del proyecto 02 está pendiente por una restricción de escritura del conector.

Los diagramas describen la arquitectura implementada y distinguen explícitamente los esquemas PostgreSQL propuestos de los flujos Python activos.
