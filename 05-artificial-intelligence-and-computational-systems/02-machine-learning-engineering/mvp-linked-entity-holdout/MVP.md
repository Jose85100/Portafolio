# MVP
Qué es: split offline por componentes conectados de identidades provistas.
Comando único: `bash run.sh` desde esta carpeta.
Salida: CSV/JSON, figura SVG, notebook con resultados y tests.
No cubre entity resolution, etiquetas, causalidad, modelos predictivos, tiempo, privacidad, clusters grandes ni asignación incremental estable.
Criterio continuar: cero cortes de vínculos declarados. Ajustar: grupos gigantes o imbalance. Cerrar despliegue: vínculos desconocidos/futuros o test vacío. No autorizado para producción.

Extensión30 en la misma línea: `bash run_balancing.sh`; DP clásica minimiza desviación de masa conservando componentes. Salidas results/balancing30/ y notebook_balancing.ipynb. Guarda las limitaciones29, añade guardias2000 filas/100componentes y rechazo de una sola componente. No garantiza fracción exacta ni rendimiento predictivo.

## Incremento31 — grafo adjudicado

Qué: `src/graph_audit.py` compara clausuras observadas/adjudicadas y asignación congelada, devuelve dataclass tipada con conteos de pares y filas expuestas. Comando: `bash run_graph_audit.sh`. Salida: `results/graph31/raw.csv`, summary.json, scale.json, mechanism.png y cost.png, notebook_graph_audit.ipynb con outputs. No infiere identidades, acepta adjudicación parcial, mide AUC ni certifica independencia empírica. Python3.12, pip acceso inicial, dependencias fijadas; ejecución notebook IPython en proceso, no kernel aislado. Prototipo experimental ejecutado; revisión y publicación separadas en informe consolidado31. No operacional.
