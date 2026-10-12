# Macro Data Lakehouse

Almacén de series macroeconómicas con vintages y consultas point-in-time sin look-ahead.

## Contrato

**Entrada:** CSV con campos `series_id,observation_date,release_date,value` (o tareas declaradas en Python para el orquestador).

**Salida:** resultados estructurados, verificables y reproducibles. Las implementaciones usan exclusivamente Python estándar.

## Ejecución

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/02-macro-data-lakehouse/tests -v
```

## Alcance y límites

Prototipo funcional de referencia: no incluye credenciales, conectores productivos, infraestructura cloud ni garantías SLA. Los datos de ejemplo son sintéticos. No usar con datos confidenciales sin controles de acceso y cifrado.

## Diseño

Separa validación de entrada, lógica de negocio y pruebas. Los algoritmos deben ser determinísticos y fallar ante esquemas o estados inválidos.
