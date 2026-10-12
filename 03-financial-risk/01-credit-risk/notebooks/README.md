# Notebooks reproducibles

Los notebooks existentes son material educativo independiente. Esta guía define cómo un notebook nuevo puede integrarse con la capa transversal sin convertirse en un proceso productivo.

1. Fijar semilla, dependencias y `dataset_version` en la primera celda.
2. Declarar `synthetic=true`; abortar si no lo es.
3. Leer un snapshot inmutable y escribir resultados con `run_id` nuevo.
4. Mostrar controles: tamaño de población, nulos, rangos de PD/LGD/EAD y conciliación de pérdida esperada.
5. Exportar únicamente tablas agregadas o IDs sintéticos. No guardar datos de fila fuera del entorno sandbox.

Plantilla de metadatos:

```json
{"contract_version":"1.0.0","dataset_version":"synthetic-2026-10-12","model_version":"demo-1.0.0","seed":20261012,"synthetic":true}
```

Un resultado reproducible debe poder reconstruirse con el mismo manifiesto, semilla y versión de código. Un notebook no aprueba crédito ni reemplaza validación de modelos.
