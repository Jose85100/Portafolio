# Rare-Event Geometry & Importance Sampling

**Estado: S2 — prototipo ejecutable (2026-10-13).** Alcance: auditoría unidimensional
con verdad conocida; no valida el programa completo ni demuestra un algoritmo nuevo.

## Pregunta
¿Cuándo un desplazamiento gaussiano hacia una cola oculta el error al estimar un evento de dos colas?

## Reproducir con un comando
Desde esta carpeta, Python 3.11+ y `make`:
```bash
make run
```
Crea un entorno local, instala versiones fijadas, ejecuta lint, mypy, pruebas,
cobertura, benchmark y notebook. Requiere internet para instalar dependencias.
Configuración en `config.json`; método y resultados en [informe.md](informe.md).

## Estructura
- `src/estimators.py`: estimadores y momentos poblacionales.
- `src/benchmark.py`: réplicas, comparación y figuras.
- `tests/`: invariantes, edge cases y property-based.
- `benchmarks/`: evidencia cruda, resumen, cobertura y figura.
- `notebook.ipynb`: resultados con outputs ejecutados.
- `referencias.bib`: cinco referencias verificadas; novedades y límites en `MVP.md`.

## Baselines y contrato
Monte Carlo directo, tilt de una cola, mezcla balanceada y mezcla defensiva.
Todos usan el mismo N y 40 semillas independientes por escenario; el costo
computacional también se reporta. El tilt simple es una ablación negativa apropiada
para una cola, no un baseline competitivo diseñado para ambas colas.

## Entorno y tests
Linux/macOS, Python 3.11+, make. Versiones directas fijadas en requirements.txt;
no hay lock transitivo ni imagen Docker. Comando de pruebas aislado:
`.venv/bin/python -m pytest --cov=src.estimators tests`.
No extrapolar precisión a carteras reales ni dimensiones mayores.
