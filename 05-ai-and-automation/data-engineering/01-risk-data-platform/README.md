# Risk Data Platform

## Por qué existe

El objetivo es reconstruir la posición de una cartera en una fecha de corte. Una entrada repetida no debe cambiar el resultado; dos valores distintos para el mismo crédito y fecha son un conflicto que requiere revisión.

## Qué hay implementado

- **Python:** [`risk_data_platform.py`](risk_data_platform.py), motor de referencia y validaciones.
- **SQL:** [`sql/schema.sql`](sql/schema.sql), definición de tablas, restricciones e índices para PostgreSQL.
- **C++17:** [`cpp/loan_snapshot.cpp`](cpp/loan_snapshot.cpp), ejecutable independiente para procesamiento de datos.
- **Pruebas:** [`tests/test_project.py`](tests/test_project.py), casos normales y entradas adversas.
- **Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), decisiones de diseño y diagramas Mermaid.

## Entrada y resultado

CSV: loan_id,as_of_date,principal,days_past_due.

El módulo produce resultados determinísticos para los datos y parámetros suministrados. No hay conectores a fuentes productivas ni credenciales en este repositorio.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/01-risk-data-platform/tests -v
```

## Qué falta resolver

El script Python usa Decimal y publica JSON con reemplazo atómico. El CLI C++ recibe importes en centavos enteros; no comparten todavía una capa de integración.

Las pruebas unitarias verifican casos específicos; no demuestran capacidad productiva, escalabilidad ni cumplimiento de un SLA. Antes de usar datos sensibles se necesitan controles de acceso, gestión de secretos y una revisión de seguridad.
