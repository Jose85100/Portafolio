# Data Quality & Lineage Engine

## Por qué existe

Antes de usar un dataset en un modelo necesito saber qué reglas incumple y qué archivo exacto fue evaluado. Las reglas generan incidencias por fila y el manifiesto incorpora un hash del contenido.

## Qué hay implementado

- **Python:** [`quality_lineage.py`](quality_lineage.py), motor de referencia y validaciones.
- **SQL:** [`sql/schema.sql`](sql/schema.sql), definición de tablas, restricciones e índices para PostgreSQL.
- **Pruebas:** [`tests/test_project.py`](tests/test_project.py), casos normales y entradas adversas.
- **Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), decisiones de diseño y diagramas Mermaid.

## Entrada y resultado

CSV arbitrario y reglas Python: field,op y value cuando corresponda.

El módulo produce resultados determinísticos para los datos y parámetros suministrados. No hay conectores a fuentes productivas ni credenciales en este repositorio.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/03-data-quality-lineage/tests -v
```

## Qué falta resolver

Un hash demuestra igualdad de bytes, no la veracidad del dato. El linaje SQL propuesto aún no está conectado al validador CSV.

Las pruebas unitarias verifican casos específicos; no demuestran capacidad productiva, escalabilidad ni cumplimiento de un SLA. Antes de usar datos sensibles se necesitan controles de acceso, gestión de secretos y una revisión de seguridad.
