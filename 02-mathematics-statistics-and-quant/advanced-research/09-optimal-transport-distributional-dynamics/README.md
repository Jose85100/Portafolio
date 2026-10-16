# Optimal Transport & Distributional Dynamics

**Madurez: S2 — prototipo acotado (2026-10-15).** Factibilidad y estabilidad del
transporte balanceado discreto; no valida el programa completo ni demuestra un algoritmo nuevo.

## Pregunta
¿Cómo evitar interpretar un costo Sinkhorn bajo pero infactible como una mejora?

## Reproducir con un comando
Desde esta carpeta, Linux/macOS con Python 3.11+, make e internet para pip:
```bash
make run
```
Crea un entorno local, instala versiones directas fijadas, ejecuta Ruff/mypy/tests,
benchmark, notebook e informe. Make fija BLAS/OMP a un hilo. Sin lock transitivo
ni imagen Docker: estas instrucciones y requirements.txt definen el entorno.

## Modelo y baselines
W2² discreto con costo cuadrático, masas normalizadas y balanceadas. Métodos:
Sinkhorn directo, Sinkhorn logarítmico y reparación de marginales. Comparadores:
LP HiGHS no regularizado y acoplamiento monótono ponderado 1D.
Se conservan por separado costo crudo, residuo, costo reparado, cotas numéricas,
convergencia, error contra LP, tiempo y memoria. Reparación no implica optimalidad.

## Artefactos
- `config.json`: tamaños, epsilons, seeds y gates anteriores al benchmark.
- `src/transport.py`: kernel, reparación y diagnóstico primal-dual.
- `src/reference.py`: LP y referencia monótona independiente 1D.
- `src/benchmark.py`: casos sintéticos y contraejemplo con datos guardados.
- `tests/`: invariantes, property-based, casos límite y fórmulas analíticas.
- `benchmarks/`: CSV, JSON, NPZ, figura, pruebas y cobertura.
- `notebook.ipynb`: cuatro celdas realmente ejecutadas, outputs visibles.
- `informe.md`, `referencias.bib`, `MVP.md`: análisis, cinco citas reales y alcance.

## Tests aislados
```bash
.venv/bin/python -m pytest --cov=src.transport --cov=src.reference tests
```
La cobertura se limita a esos dos módulos. El notebook se ejecuta mediante
IPython en proceso para evitar depender de puertos TCP, y puede reejecutarse
como notebook Python estándar.

## Límites explícitos
API: masas no negativas con suma a distancia ≤1e-12 de 1 (normalización explícita);
costos finitos en [0,1e6]; epsilon en [1e-8,1e4]; soporte de peso cero permitido.
Estos rangos no garantizan precisión/convergencia para toda combinación.
Benchmark solo 1D, n≤64 y epsilon≥.005. Las cotas usan float64 y tolerancias,
no aritmética de intervalos. Sin JKO, causalidad, OT no balanceado, epsilon-scaling
ni divergencias Sinkhorn des-sesgadas. El contrato EL=83 y los programas previos
no se modifican. Ver los fallos y la no convergencia en informe.md.
