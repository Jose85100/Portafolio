# Workflow Orchestrator

## Por qué existe

Los pipelines fallan y se vuelven a ejecutar. Este orquestador ordena tareas por dependencias, detecta ciclos y guarda un checkpoint para no repetir las que terminaron correctamente.

## Qué hay implementado

- **Python:** [`workflow_orchestrator.py`](workflow_orchestrator.py), motor de referencia y validaciones.
- **SQL:** [`sql/schema.sql`](sql/schema.sql), definición de tablas, restricciones e índices para PostgreSQL.
- **Pruebas:** [`tests/test_project.py`](tests/test_project.py), casos normales y entradas adversas.
- **Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), decisiones de diseño y diagramas Mermaid.

## Entrada y resultado

Tareas Python con identificador, dependencias y reintentos.

El módulo produce resultados determinísticos para los datos y parámetros suministrados. No hay conectores a fuentes productivas ni credenciales en este repositorio.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/05-workflow-orchestrator/tests -v
```

## Qué falta resolver

El checkpoint local no garantiza exactamente una ejecución de efectos externos. Las operaciones con side effects deben diseñarse como idempotentes.

Las pruebas unitarias verifican casos específicos; no demuestran capacidad productiva, escalabilidad ni cumplimiento de un SLA. Antes de usar datos sensibles se necesitan controles de acceso, gestión de secretos y una revisión de seguridad.
