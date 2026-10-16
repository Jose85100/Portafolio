# Distributionally Robust Optimization

**Madurez: S2 — primer prototipo acotado (2026-10-16).** Expectativa robusta KL en
soporte finito. No es aún Wasserstein DRO ni una solución a la calibración del radio.

## Pregunta
¿Cuándo una aproximación media-varianza subestima el peor caso KL y altera una decisión?

## Reproducir en un comando
Desde esta carpeta, Linux/macOS, Python 3.11+, make e internet para pip:
```bash
make run
```
Instala versiones directas fijadas, ejecuta Ruff/mypy/tests, benchmark, notebook e
informe. BLAS/OMP a un hilo. No hay lock transitivo ni imagen Docker.

## Modelo y comparación
Supremo de qᵀloss sujeto a KL(q||p)≤rho y q en el simplex, p_i>0.
Inclinación exponencial centrada y bisección con diagnóstico primal-dual.
Baselines: SLSQP primal con restricciones explícitas, media nominal y expansión
de radio pequeño media+sqrt(2*rho*varianza). Un oracle de Bernoulli independiente
busca directamente la probabilidad. Dos acciones ilustran ventajas y costos
del minimax; no se hacen recomendaciones financieras.

## Artefactos
- `config.json`: casos y gates anteriores a los experimentos.
- `src/kl_robust.py`: nominal, constantes, interior y saturación.
- `src/reference.py`: SLSQP con variantes reejecutables y oracle binario.
- `src/benchmark.py`: datasets, pesos, precisión, recursos y decisiones.
- `tests/`: fórmulas, invariantes, límites y Hypothesis.
- `benchmarks/`: CSV/JSON, datos, pesos, figura y evidencia de pruebas.
- `benchmarks/initial_baseline/`, `benchmarks/two_start_baseline/`:
  dos ejecuciones fallidas preservadas; los umbrales no se relajaron.
- `notebook.ipynb`: cuatro celdas realmente ejecutadas.
- `informe.md`, `referencias.bib`, `MVP.md`: crítica, cinco citas y alcance.

## Tests aislados
```bash
.venv/bin/python -m pytest --cov=src.kl_robust --cov=src.reference tests
```
La cobertura corresponde a esos dos módulos, no a toda la aplicación.
El notebook ejecuta Python en proceso vía IPython, con outputs reales; no necesita
puertos TCP y es reejecutable como notebook Python estándar.

## Entorno, dominio y límites
p_i≥1e-12, suma a distancia ≤1e-12 de 1 (normalización explícita), |loss_i|≤1e6.
Radio cero o entre 1e-10 y 100. Radios positivos menores se rechazan, al igual
que probabilidades nominales cero; soporte desconocido no queda protegido.
Los rangos de entrada no garantizan precisión universal. Cotas numéricas
float64, no certificación formal. SLSQP usa suelo interior q_i≥1e-12*p_i y un
refinamiento desde su propia mejor solución, sin usar el kernel para inicializarlo.
Mensajes y advertencias se conservan. Radio exógeno: sin cobertura estadística,
no estacionariedad estimada, optimización continua ni Wasserstein. Ver informe.md.
EL=83 y los programas anteriores no se modifican.
