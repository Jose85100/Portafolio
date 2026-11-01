# MVP
Qué es: split offline por componentes conectados de identidades provistas.
Comando único: `bash run.sh` desde esta carpeta.
Salida: CSV/JSON, figura SVG, notebook con resultados y tests.
No cubre entity resolution, etiquetas, causalidad, modelos predictivos, tiempo, privacidad, clusters grandes ni asignación incremental estable.
Criterio continuar: cero cortes de vínculos declarados. Ajustar: grupos gigantes o imbalance. Cerrar despliegue: vínculos desconocidos/futuros o test vacío. No autorizado para producción.

Extensión30 en la misma línea: `bash run_balancing.sh`; DP clásica minimiza desviación de masa conservando componentes. Salidas results/balancing30/ y notebook_balancing.ipynb. Guarda las limitaciones29, añade guardias2000 filas/100componentes y rechazo de una sola componente. No garantiza fracción exacta ni rendimiento predictivo.

## Incremento31 — grafo adjudicado

Qué: `src/graph_audit.py` compara clausuras observadas/adjudicadas y asignación congelada, devuelve dataclass tipada con conteos de pares y filas expuestas. Comando: `bash run_graph_audit.sh`. Salida: `results/graph31/raw.csv`, summary.json, scale.json, mechanism.png y cost.png, notebook_graph_audit.ipynb con outputs. No infiere identidades, acepta adjudicación parcial, mide AUC ni certifica independencia empírica. Python3.12, pip acceso inicial, dependencias fijadas; ejecución notebook IPython en proceso, no kernel aislado. Prototipo experimental ejecutado; revisión y publicación separadas en informe consolidado31. No operacional.

## Incremento1nov — utilidad con adjudicación parcial

Qué: API tipada `src.partial_audit.partial_audit`, cotas exactas de filas expuestas según equivalencia completa en subconjunto; no asigna identidades a desconocidos. Comando único `bash run_partial_audit.sh`, instala .venv; Python3.12+, pip inicial. Produce results/partial1101/{raw.csv,summary.json,scale.json,information.png,cost.png,tests.txt,types.txt,lint.txt,versions.txt,environment.json}, notebook_partial_audit.ipynb ejecutado y visible. Reuso `PYTHON="$PWD/.venv/bin/python" SKIP_INSTALL=1 bash run_partial_audit.sh`.36 tests pasan; fórmulas y límites en derivacion1101.md. No cubre enlaces positivos incompletos, adjudicación errónea, temporalidad, AUC, validez empírica ni operación. No kernel Jupyter aislado; ejecución IPython secuencial real en proceso,2 figuras inspeccionadas.
