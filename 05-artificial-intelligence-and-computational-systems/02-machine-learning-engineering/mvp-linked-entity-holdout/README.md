# Holdout por identidades vinculadas

MVP offline ejecutable del pilar02. Pregunta: ¿agrupar solo la clave primaria deja cadenas de identidad entre entrenamiento y test? Cierre transitivo de vínculos explícitos y holdout determinista por componentes; algoritmo conocido, integración incremental local. No entrena modelos ni infiere vínculos.

Desde esta carpeta: `bash run.sh` instala dependencias fijadas en .venv, ejecuta tests/lint/tipos, benchmark y notebook. Python3.12+ y acceso pip inicial requeridos. Reuso auditado: `PYTHON=/workspace/scratch/6c8b818bd733/ia28-env/bin/python SKIP_INSTALL=1 bash run.sh`.

Salidas: results/inputs.json, raw.csv, summary.json y leakage.svg; notebook.ipynb con outputs visibles. Notebook ejecutado mediante IPython secuencial en proceso; no kernel Jupyter independiente. Números deterministas: filas108/144 componentes cortados; clave primaria70/144; componente0/144. 12 seeds sobre el mismo corpus no son12 datasets independientes; sin intervalos inferenciales.

Todas políticas ordenan grupos por SHA256(seed:clave), reservan mitad de grupos. El baseline fila conserva18/36 train; primaria17–20/36; componente18/36 por grupos artificialmente iguales. Baselines difieren en unidad de partición: no son óptimos contra los que probar superioridad predictiva. Coste solo splitter incluyendo validación compartida; no incluye I/O/auditoría ni entrenamiento. Links se suministran antes del split, sin etiquetas. El uso de información del futuro para generarlos invalidaría una evaluación temporal.

Madurez local: prototipo experimental ejecutado, no validado en datos reales ni operacional; no se equipara S2 a M2. Sin cambios en shared, contratos ni aplicaciones riesgo. Ver informe.md (14 puntos) y referencias.bib. Cobertura de líneas no medida; no C++.

## Extensión acumulativa30: tamaños desiguales

El negativo explícito29 (componentes iguales) se aborda en la misma línea. `bash run_balancing.sh` instala el entorno fijado, ejecuta todos los tests29+30, lint/tipos,50 comparaciones sintéticas+6 mediciones de escala y notebook_balancing.ipynb (6celdas ejecutadas IPython en proceso). No modifica las salidas29. Derivación y unidades en derivacion30.md; matriz prior_art30.md, research-log.md y roadmap.md. Código src/balancing.py aplica DP subset-sum clásica con guardias; no es una nueva técnica ML.

Resultados:20/25 mejoras,5 empates,0 empeoramientos;0 cortes para ambas políticas. Desviación media3.5067→2.0133 filas. Negativo gigante:13.5 filas irreducibles. Experimentos sintéticos sin labels; no AUC ni escalabilidad industrial. La selección basada en tamaños usa solo metadata del snapshot; no resolver temporalidad ni calidad de vínculos. Madurez local experimental ejecutada, no validada/operacional. Ver informe_balancing30.md y results/balancing30/.

```mermaid
flowchart TD
    A["Snapshot: filas y vínculos declarados"] --> B["Componentes29"]
    B --> C{"Dos o más componentes y dentro de guardias"}
    C -->|No| D["Error explícito: no holdout factible admitido"]
    C -->|Sí| E["DP de masas alcanzables"]
    E --> F["Asignación indivisible y auditoría de cortes"]
    F --> G["Reportar desviación residual y decidir utilidad"]
```

La última decisión es humana: el código no acepta automáticamente un split útil por tener0 cortes.

## Extensión31: auditar el grafo, además del split

`bash run_graph_audit.sh` instala y reproduce28 tests (21 regresión+7 nuevos), lint/tipos,144 escenarios/políticas registrados, escala del auditor28–28000 filas y notebook_graph_audit.ipynb ejecutado6 celdas con2 figuras visibles. Salidas `results/graph31/` CSV/JSON/PNG/logs. Reúso entorno: `PYTHON="$PWD/.venv/bin/python" SKIP_INSTALL=1 bash run_graph_audit.sh`.

Una segunda partición adjudicada completa permite distinguir fragmentación y sobre-unión. **Cero cortes declarados no garantiza cero fuga adjudicada**: en faltantes DP30 tiene0 cortes declarados y fuga verdadera12/12; en mixto logra balance perfecto pero expone28/28 filas. No es certificación de ML ni datos reales. El oráculo conoce verdad privilegiada y puede cortar el grafo declarado; no es baseline desplegable. Ver informe_graph31.md, derivacion31.md, prior_art31.md. No se cambian contratos/shared ni se elimina notebook anterior. Auditoría de ingeniería sobre la misma línea, sin claim de algoritmo nuevo.

## Incremento1nov: adjudicación parcial con cotas y abstención

El mismo programa acepta ahora equivalencia **completa entre filas adjudicadas de un subconjunto**, incluidas identidades distintas; no solo enlaces positivos incompletos. `bash run_partial_audit.sh` instala dependencias fijadas, ejecuta36 tests (28 regresión+8 nuevos), Ruff/tipos,480 comparaciones, escala del auditor y notebook_partial_audit.ipynb (6 celdas ejecutadas,2 figuras visibles). Datos sintéticos, sin AUC ni afirmación de independencia empírica. Salidas `results/partial1101/` CSV/JSON/PNG/logs; deriva fórmula y extremos alcanzables en derivacion1101.md, derivaciones también en notebook.

Bajo el contrato, calcula [L,H] de filas expuestas sobre todas las completaciones posibles;5508 configuraciones pequeñas verificadas contra enumeración independiente. A75% de cobertura, train-first obtiene anchura media15.625 filas frente21.395833 de baseline seguro, pero mantiene24/48 abstenciones. En otros regímenes no mejora la cota: resultado negativo conservado. Sin adjudicación devuelve[0,n], no extrapola; si la adjudicación es errónea las cotas pueden fallar. Madurez local experimental, no operación/validación empírica. Auditor31 permanece intacto y se recupera en el caso completo. Ver informe_partial1101.md, prior_art1101.md y roadmap.

```mermaid
flowchart TD
    A["Split congelado del snapshot observado"] --> B["Equivalencia adjudicada parcial y externa"]
    B --> C["Extremos de exposición sobre completaciones"]
    C --> D["Detectar, cero condicionado o abstenerse"]
```

## Incremento2nov: semántica y disponibilidad del snapshot

`bash run_snapshot_gate.sh` instala dependencias fijadas y reproduce46 tests (36 regresión+10 nuevos), Ruff/tipos,144 casos/6 políticas (864 CSV),12 mediciones de coste y notebook_snapshot_gate.ipynb ejecutado con6 celdas y2 figuras visibles. `src/snapshot_gate.py` añade un contrato local sobre adjudicación: fuente/esquema, equivalencia completa en subconjunto, effective_at/available_at≤cutoff con UTC; bloquea incompatibilidades **sin calcular cotas**. No modifica shared ni contratos de otros programas.

Resultados de conformidad sintética: gate y referencia as-of coinciden en144/144,8 admisiones elegibles y0 falsos admitidos/rechazados. Solo fecha efectiva admite4 snapshots no disponibles; solo semántica admite10 incompatibles. No es nuevo algoritmo ML ni estudio empírico. Un hash canónico vincula entradas/asignación/corte, y verify_manifest detecta modificaciones sin actualizar digest; **no autentica fuente ni fechas**. Negativo conservado: declaraciones falsas pueden pasar y dar cota0 frente8 filas expuestas reales.

Salida `results/snapshot1102/` CSV/JSON/PNG/manifests/logs, derivacion1102.md (fórmulas también en notebook), prior_art1102.md cinco fuentes verificadas e informe_snapshot1102.md14p. Notebook ejecutado IPython en proceso, no kernel aislado ni frontend Jupyter completo. Prototipo experimental, sin validación empírica/operación ni garantía de temporalidad del pipeline de features. El pilarML continúa para cerrar la precondición bloqueante1101; rotación y datos reales siguen pendientes.

```mermaid
flowchart TD
    A["Snapshot adjudicado con fuente y dos fechas"] --> B{"Metadatos prospectivos elegibles"}
    B -->|No| C["Bloqueo con motivos, sin cotas"]
    B -->|Sí| D["Auditor parcial1nov y manifiesto canónico"]
```
