# Weighted Tail Underflow Guard

MVP del 2026-10-15: entrada Python protegida frente a underflow de NumPy, con rechazo explícito o fallback racional. Continúa los PR #32 y #35, ya integrados. No modifica el baseline: su comportamiento y sus límites permanecen auditables.

## Instalación y reproducción: un comando

Desde la raíz del **repo completo**, con Python 3.12 y venv:

```bash
bash 03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/run.sh
```

Instala el entorno local fijado en requirements.lock.txt, ejecuta Ruff, mypy (src y benchmarks), pytest con cobertura de src.guard, 388 casos numéricos, benchmark y notebook con salidas reales. Requiere internet para la instalación inicial; experimentos sin red ni datos privados. Verificado en Linux x86-64, Python 3.12.14, NumPy 2.1.3. No se promete reproducción bit a bit de tiempos ni de aritmética en plataformas no verificadas.

## API y contrato

```python
from src.guard import guarded_tail
r = guarded_tail([1e308, 0.0], weights=[1e-300, 1e300])
print(r.es, r.backend, r.fallback_reason)  # ~4e-291, fraction, underflow...
```

- Pérdidas finitas, positivas/negativas; pesos no negativos y normalizados internamente; inputs interpretados como binary64, no decimales ideales.
- El camino habitual ejecuta el motor real del PR #32 dentro de `np.errstate(under='raise')`, restaurando el estado previo al salir.
- `policy='exact'` (default): recalcula desde **los inputs originales**, nunca desde pesos ya dañados, con Fraction y masa de cola fraccionaria.
- `policy='raise'`: lanza TailUnderflowError. También se rechaza un fallback que exceda max_exact_scenarios=4096 filas de entrada. El presupuesto limita sorpresas de costo, no es un umbral estadístico.
- El resultado informa backend, motivo, exact_es (solo fallback), output_rounds_to_zero. Si este último flag es True, **no debe consumirse solo r.es**: el racional no nulo no cabe en float; hay que usar la fracción, cambiar escala/unidad o rechazar el resultado.
- El guard captura eventos de underflow de NumPy; **no es un detector universal de todo error de redondeo**. El camino float64 conserva las limitaciones de precisión del baseline.

## Verificación y outputs

- src/guard.py: cálculo exacto, guard y políticas; src/sources.py: comparadores reales, sin demos.
- tests/: analíticos, inputs inválidos, presupuesto, restauración de errstate y dos propiedades generativas de 100 ejemplos cada una.
- benchmarks/config.json: seed, exponentes, tamaños y repeticiones fijados.
- results/accuracy.csv y fixtures.json: referencia hinge racional independiente importada del aporte C++, numeradores/denominadores, motivos y flags.
- results/performance.csv: tiempo separado de tracemalloc, orden de métodos aleatorizado por réplica con seed; pico de asignaciones Python/NumPy, **no RSS ni memoria nativa completa**. Se conserva la medición piloto con orden fijo en initial-fixed-order-performance.csv.
- results/comparison.svg: pérdidas a cero y costo del fallback; notebook.ipynb: tres celdas ejecutadas con IPython en proceso, capturando stdout/display_data reales sin sockets.
- results/tests.txt, coverage.json, lint.txt y types.txt: evidencia de ejecución. La cobertura declarada es del guard, no todo el pipeline.
- informe.md, referencias.bib y MVP.md: método, resultados, límites y ocho referencias primarias.

Comandos individuales después de instalar: `.venv/bin/python -m pytest -q`, `.venv/bin/python -m benchmarks.run`, `.venv/bin/python benchmarks/notebook.py`.

## Equidad y alcance

Se ejecuta el baseline real, no uno artificialmente debilitado. La referencia minimiza la función hinge de CVaR en aritmética racional; el fallback integra átomos ordenados en racionales: implementaciones distintas. La comparación incluye always_exact como ablación: el fallback puede ser mucho más lento que el baseline, que en los casos extremos devuelve un valor incorrecto.

Los casos adversariales no estiman la frecuencia de fallos en mercados reales. No hay pronóstico, calibración de pesos, IFRS 9/SFC/FRTB ni prueba de superioridad económica. No se modifica C++, por lo que no se ejecutan nuevos sanitizers C++ en este ciclo. No se altera la semántica de los aportes anteriores ni se garantiza soporte de sus futuros cambios sin revisar esta auditoría.
