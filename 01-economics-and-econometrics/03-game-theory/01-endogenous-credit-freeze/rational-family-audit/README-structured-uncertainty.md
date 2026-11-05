# Shocks correlacionados y regret

Extiende `rational-family-audit` comparando incertidumbre rectangular independiente con un shock común por acción rival. La derivación está en `structured-uncertainty-note.md`; MVP y límites en `structured-uncertainty-MVP.md`.

Desde esta carpeta: `bash run_structured_uncertainty.sh`. Este comando instala dependencias fijadas en `.venv`, ejecuta pruebas focales, lint y tipos, genera resultados y ejecuta `notebook_structured.ipynb` de arriba a abajo mediante el ejecutor en proceso `benchmarks/execute_structured_notebook.py`. Para la suite común del programa: `python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v` desde la raíz del repositorio con el entorno instalado.

La matriz de antecedentes está en `prior_art_structured.md`, BibTeX en `references_structured.bib` y el informe crítico con resultados negativos en `informe_structured.md`. `config_structured_uncertainty.json` fija el escenario y deltas; la plataforma efectiva queda en `results/structured_uncertainty/metrics.json`.

Los datos son sintéticos. El resultado es una cancelación algebraica bajo el supuesto explícito de shock común por columna; no implica que errores reales tengan esa estructura.
