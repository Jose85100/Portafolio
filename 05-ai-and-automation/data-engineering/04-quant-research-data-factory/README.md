# Quant Research Data Factory

## Por qué existe

El error más costoso en un backtest puede ser usar información que todavía no existía. Aquí separo fecha de característica y final del horizonte de predicción, y purgo etiquetas que se solapan con la prueba.

## Qué hay implementado

- **Python:** [`quant_data_factory.py`](quant_data_factory.py), motor de referencia y validaciones.
- **SQL:** [`sql/schema.sql`](sql/schema.sql), definición de tablas, restricciones e índices para PostgreSQL.
- **C++17:** [`cpp/rolling_features.cpp`](cpp/rolling_features.cpp), ejecutable independiente para procesamiento de datos.
- **Pruebas:** [`tests/test_project.py`](tests/test_project.py), casos normales y entradas adversas.
- **Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), decisiones de diseño y diagramas Mermaid.

## Entrada y resultado

CSV: asset,date,price.

El módulo produce resultados determinísticos para los datos y parámetros suministrados. No hay conectores a fuentes productivas ni credenciales en este repositorio.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/04-quant-research-data-factory/tests -v
```

## Qué falta resolver

El prototipo Python presupone que el precio ya era observable en su fecha. La disponibilidad real del dato debe controlarse antes de utilizarlo en investigación aplicada.

Las pruebas unitarias verifican casos específicos; no demuestran capacidad productiva, escalabilidad ni cumplimiento de un SLA. Antes de usar datos sensibles se necesitan controles de acceso, gestión de secretos y una revisión de seguridad.
