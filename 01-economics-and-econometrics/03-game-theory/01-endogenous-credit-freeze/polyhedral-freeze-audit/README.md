# Polyhedral Freeze Audit — familias de equilibrio, S2

Representación racional del conjunto de equilibrios de comportamiento del mismo
juego bayesiano de dos prestamistas. Visita los 81 patrones y representa cada región
factible como producto de dos poliedros bidimensionales acotados. Calcula vértices,
restricciones y dimensión afín real; no deduce dimensión sólo del rango de ecuaciones.

## Comando único

Desde la raíz del repo, Python 3.12, Bash, venv y acceso inicial a PyPI:

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/polyhedral-freeze-audit/reproduce.sh
```

Instala las dependencias fijadas, ejecuta Ruff/mypy, tests nuevos con cobertura,
las suites mixtas/puras/comunes, benchmarks y notebook. El notebook ejecuta celdas
reales en IPython in-process, sin kernel de red ni outputs inventados.
`requirements.txt` fija dependencias directas; `environment-lock.txt` registra las
versiones completas observadas. Instrucciones venv reproducibles; Docker no requerido.

## Entregables

- `src/polyhedra.py`: H/V-poliedros racionales 2D, dimensiones, producto, inclusión,
  poda de celdas contenidas, regret exacto y serialización.
- `tests/`: 10 tests, incluidas propiedades de vértices/baricentros y rectángulos.
- `results/cells.json`: restricciones y vértices como cadenas racionales exactas.
- `results/summary.csv`, `samples.csv`, `lp_oracle.csv`, `timing.csv`, `metadata.json`.
- `results/family.png` y `notebook.ipynb` ejecutado con salidas visibles.
- `informe.md`, `MVP.md`, `referencias.bib`, `prior_art_search.md`.

## Interpretación y límites

Las celdas máximas son máximas por inclusión entre los productos enumerados;
NO son necesariamente componentes conexas ni una partición disjunta.
En cada factor, todos los puntos son combinaciones convexas de sus vértices.
La unión de productos representa estrategias de comportamiento; no una medida de
selección entre equilibrios ni el conjunto de distribuciones sobre planes puros.
Se aprovechan específicamente dos jugadores/dos tipos y payoff afín. No solver genérico.

Se conserva S2 del componente finito. Juego global continuo, identificación real,
balances bancarios, intervención óptima y validación S3/S4 siguen fuera del alcance.
