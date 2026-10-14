# Mixed Freeze Audit — extensión ejecutable S2

Enumera equilibrios bayesianos en estrategias de comportamiento del mismo juego
finito de dos prestamistas del MVP anterior. Examina 81 patrones de soporte;
verifica incentivos por tipo y rechaza los casos con soporte singular factible.
No convierte un continuo de equilibrios en una lista finita ficticia.

## Comando único

Desde la raíz del repositorio, con Python 3.12, Bash, venv y PyPI inicial:

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/mixed-equilibrium-audit/reproduce.sh
```

Instala dependencias fijadas, ejecuta lint/type checks, tests con cobertura,
la suite pura anterior, la suite común y benchmarks; genera notebook ejecutado.
`environment-lock.txt` registra el entorno completo observado. No requiere GPU,
credenciales, microdatos ni kernel Jupyter con sockets. Se usa IPython in-process
para ejecutar y capturar las salidas reales de las celdas.

## Estructura

- `src/mixed.py`: ganancias afines, regret, soportes, LP para diagnóstico de
  singularidad, oráculo racional independiente y outcomes con randomización.
- `tests/`: unitarios, propiedades Hypothesis, degeneración y fallo de LP.
- `benchmarks/run.py`: compara con la enumeración pura del repo, precisión,
  sensibilidad, estabilidad de tolerancia y tiempo/memoria.
- `results/`: CSV crudos, JSON con config/hardware/hashes, logs y figura.
- `notebook.ipynb`: narrativa, tabla, resultados negativos, cobertura y figura.
- `informe.md`, `MVP.md`, `referencias.bib`, `prior_art_search.md`.

## Contrato numérico y alcance

`solve(Game(), tolerance=1e-10)` devuelve equilibrios aislados, incluidos puros.
`DegenerateGameError` indica que un soporte singular factible impide certificar
una lista finita; no significa que el juego carezca de equilibrio.
Resultados numéricos verificados, no prueba general de existencia o unicidad.
Se reutiliza el modelo de `../bayesian-freeze-audit/src/game.py`; no se cambia su
calibración ni su baseline. Dependencias e instrucciones venv sustituyen Docker.

Se conserva S2 del componente finito. El juego global continuo, la selección de
equilibrio y la identificación empírica siguen fuera del MVP. Los límites entre
equilibrios no son probabilidades estimadas de selección ni bienestar social.
