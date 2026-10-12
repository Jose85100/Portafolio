# Macro Data Lakehouse

## Por qué existe

Una serie macroeconómica cambia después de publicarse. Guardar solo su último valor introduce información futura en un backtest. Este ejercicio conserva cada versión y permite consultar qué estaba disponible en una fecha.

## Qué hay implementado

- **Python:** [`macro_lakehouse.py`](macro_lakehouse.py), motor de referencia y validaciones.
- **SQL:** [`sql/schema.sql`](sql/schema.sql), definición de tablas, restricciones e índices para PostgreSQL.
- **Pruebas:** [`tests/test_project.py`](tests/test_project.py), casos normales y entradas adversas.

## Entrada y resultado

series_id,observation_date,release_date,value.

El módulo produce resultados determinísticos para los datos y parámetros suministrados. No hay conectores a fuentes productivas ni credenciales en este repositorio.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/02-macro-data-lakehouse/tests -v
```

## Qué falta resolver

El prototipo almacena los vintages en SQLite. El esquema PostgreSQL modela una posible migración; no es el backend activo.

Las pruebas unitarias verifican casos específicos; no demuestran capacidad productiva, escalabilidad ni cumplimiento de un SLA. Antes de usar datos sensibles se necesitan controles de acceso, gestión de secretos y una revisión de seguridad.
