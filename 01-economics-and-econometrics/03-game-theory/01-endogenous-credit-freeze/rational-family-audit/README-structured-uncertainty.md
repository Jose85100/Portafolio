# Shocks correlacionados y regret

Extiende `rational-family-audit` comparando incertidumbre rectangular independiente con un shock común por acción rival. La derivación está en `structured-uncertainty-note.md`; MVP y límites en `structured-uncertainty-MVP.md`.

Desde esta carpeta: `python3 benchmarks/structured_uncertainty.py`. Dependencias: las fijadas por el proyecto en `requirements.txt`. Pruebas focales: `python3 -m unittest tests.test_uncertainty_structures -v`.

Los datos son sintéticos. El resultado es una cancelación algebraica bajo el supuesto explícito de shock común por columna; no implica que errores reales tengan esa estructura.
