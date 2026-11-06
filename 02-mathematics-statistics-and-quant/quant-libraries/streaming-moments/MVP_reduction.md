# MVP — reducción balanceada para MOMENTS

API `src.reduction.merge_balanced(states)` fusiona resúmenes `DynamicMoments` en árbol binario fijo, manteniendo la unidad común rebased por la implementación existente. Entrada vacía da identidad; una entrada no se copia. Supone particiones disjuntas. Ejecuta `bash run.sh`; agrega `results/reduction_raw.csv`, `reduction_summary.json`, `reduction_order.png` y `notebook_reduction.ipynb` ejecutado. No garantiza independencia de permutación, exactitud real-aritmética, deduplicación, mejora de velocidad ni uso operacional.
