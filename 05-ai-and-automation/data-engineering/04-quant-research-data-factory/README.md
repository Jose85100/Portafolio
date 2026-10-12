# Quant Research Data Factory

Constructor de características as-of y etiquetas forward con separación temporal estricta.

## Contrato

**Entrada:** CSV con campos `asset,date,price` (o tareas declaradas en Python para el orquestador).

**Salida:** resultados estructurados, verificables y reproducibles. Las implementaciones usan exclusivamente Python estándar.

## Ejecución

```bash
python3 -m unittest discover -s 05-ai-and-automation/data-engineering/04-quant-research-data-factory/tests -v
```

## Alcance y límites

Prototipo funcional de referencia: no incluye credenciales, conectores productivos, infraestructura cloud ni garantías SLA. Los datos de ejemplo son sintéticos. No usar con datos confidenciales sin controles de acceso y cifrado.

## Diseño

Separa validación de entrada, lógica de negocio y pruebas. Los algoritmos deben ser determinísticos y fallar ante esquemas o estados inválidos.
