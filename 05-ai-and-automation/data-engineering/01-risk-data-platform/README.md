# Risk Data Platform

Pipeline D+1 de cartera con esquema tipado, deduplicación determinística, conciliación y snapshot atómico.

## Contrato

**Entrada:** CSV con campos `loan_id,as_of_date,principal,days_past_due` (o tareas declaradas en Python para el orquestador).

**Salida:** resultados estructurados, verificables y reproducibles. Las implementaciones usan exclusivamente Python estándar.

## Ejecución

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/01-risk-data-platform/tests -v
```

## Alcance y límites

Prototipo funcional de referencia: no incluye credenciales, conectores productivos, infraestructura cloud ni garantías SLA. Los datos de ejemplo son sintéticos. No usar con datos confidenciales sin controles de acceso y cifrado.

## Diseño

Separa validación de entrada, lógica de negocio y pruebas. Los algoritmos deben ser determinísticos y fallar ante esquemas o estados inválidos.
