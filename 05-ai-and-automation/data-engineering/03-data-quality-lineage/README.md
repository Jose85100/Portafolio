# Data Quality & Lineage Engine

Reglas declarativas de calidad, perfiles y manifiesto SHA-256 de trazabilidad.

## Contrato

**Entrada:** CSV con campos `dataset,field,rule,parameter` (o tareas declaradas en Python para el orquestador).

**Salida:** resultados estructurados, verificables y reproducibles. Las implementaciones usan exclusivamente Python estándar.

## Ejecución

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/03-data-quality-lineage/tests -v
```

## Alcance y límites

Prototipo funcional de referencia: no incluye credenciales, conectores productivos, infraestructura cloud ni garantías SLA. Los datos de ejemplo son sintéticos. No usar con datos confidenciales sin controles de acceso y cifrado.

## Diseño

Separa validación de entrada, lógica de negocio y pruebas. Los algoritmos deben ser determinísticos y fallar ante esquemas o estados inválidos.
