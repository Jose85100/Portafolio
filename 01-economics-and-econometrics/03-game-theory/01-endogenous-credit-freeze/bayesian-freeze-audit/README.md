# Bayesian Freeze Audit

**S2: componente finito de Endogenous Credit Freeze.** Dos prestamistas, dos señales,
acción binaria y fundamentales binarios. Enumera los 16 perfiles de estrategias puras,
verifica regret interim, compara con mejores respuestas del núcleo común y calcula
límites de congelación entre equilibrios. No es el juego global continuo completo.

## Comando único de reproducción

Desde raíz del repositorio, Python 3.12, Bash, venv y acceso PyPI inicial:

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/bayesian-freeze-audit/reproduce.sh
```

Instala dependencias fijadas en .venv; ejecuta Ruff, mypy, tests con cobertura, suite común,
benchmark y celdas reales del notebook en IPython in-process. Un fallo detiene el comando.
No necesita credenciales, datos privados, GPU ni Jupyter con sockets.

## Artefactos

- `src/game.py`: posterior, ganancias, regret, enumeración, oracle Fraction independiente,
  mejores respuestas del repo, detección de ciclos y probabilidades de resultados.
- `tests/`: pruebas unitarias, edge cases y dos propiedades Hypothesis (100 ejemplos cada una).
- `results/main.csv`, `grid.csv`, `oracle.csv`, `costs.csv`, `tolerance.csv`.
- `results/summary.json`, `metadata.json` con seeds, CPU, hashes y configuración.
- `results/equilibria.png` y `notebook.ipynb` ejecutado con outputs visibles.
- `informe.md`, `referencias.bib`, `prior_art_search.md`, `MVP.md` y environment-lock.txt.

## Entorno reproducible

Probado con Python 3.12 en Linux x86_64; dependencias directas en requirements.txt,
versiones completas observadas en environment-lock.txt. Reproducción alternativa manual:
`python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`,
`.venv/bin/python benchmarks/run.py`. El comando único anterior incluye todas las verificaciones.
No se requiere Docker; la receta venv satisface las instrucciones de entorno reproducible.

Las métricas de congelación son condicionales al fundamental bueno, no probabilidades
estimadas de selección de equilibrio. La suma de payoffs de prestamistas no es bienestar social.
