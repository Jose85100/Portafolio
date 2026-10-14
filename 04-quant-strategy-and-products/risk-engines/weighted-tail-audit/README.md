# Weighted Tail Audit — C++17

MVP de I+D+i del 2026-10-14: ES de escenarios con probabilidades desiguales, contrato Python/C++ y validación frente a un oráculo racional independiente. Continúa el aporte Python del PR #32 (ya integrado), sin duplicarlo ni cambiar el comportamiento de `quant::tail`.

## Un comando de instalación y reproducción

Desde la raíz del repositorio completo:

```bash
bash 04-quant-strategy-and-products/risk-engines/weighted-tail-audit/run.sh
```

O desde esta carpeta: `bash run.sh`. Requiere **Linux, Python 3.12 con venv, g++, gcov y make**. Entorno verificado: Ubuntu/glibc, GCC/gcov 13.3.0, x86-64. Las herramientas Python, CMake, Clang-Tidy y Clang-Format se instalan en `.venv` con versiones fijadas en requirements.txt. Internet solo es necesario para la instalación inicial. El comando compila Release, ejecuta tests, lint y tipos, el benchmark, ASan/UBSan, cobertura GCC y la regresión del motor original. No descarga datos ni usa cuentas privadas.

No se garantiza reproducción bit a bit en otros compiladores o arquitecturas; `long double` depende de la plataforma. No usar `-ffast-math`. Los tiempos y RSS varían con hardware/carga. GCC/gcov deben corresponder a la misma versión. Solo se validó Linux; no se afirma validación Windows/macOS.

## API y convenciones

API pública en `../include/quant/weighted_tail.hpp`:

```cpp
#include "quant/weighted_tail.hpp"
const auto risk = quant::weighted_tail({{0.0, 99.0}, {100.0, 1.0}}, 0.975);
// risk.es ~= 40; risk.var = 0; risk.mean = 1
```

Pérdidas positivas representan costos; ganancias pueden ser negativas. Pesos finitos, no negativos y no necesariamente normalizados. Se excluyen escenarios de peso cero. VaR es la inversa izquierda de la CDF; ES integra la masa 1-alpha con frontera fraccionaria. El motor conserva sumas en precisión extendida, escala pesos/pérdidas y usa suma compensada. Complejidad O(n log n), memoria O(n).

## Comparadores y experimentos

- Oráculo independiente: minimizar la función hinge de Rockafellar–Uryasev en los átomos, con `fractions.Fraction`, preservando exactamente los inputs binarios.
- Paridad: ejecución de la implementación Python real del aporte anterior, cargada desde su ruta actual; hashes en metadata.
- Baseline equivalente: pesos enteros 1–8 se expanden en repeticiones y se ejecuta `quant::tail` real sobre esa distribución equiprobable. El objetivo ES es el mismo; su VaR interpolado es una convención distinta y no se compara.
- Ablación negativa: ignorar pesos y ejecutar el mismo `quant::tail` sin expansión; no se presenta como competidor válido del objetivo ponderado.
- 207 fixtures, con 200 generados por seed=20261014 y siete casos diseñados; 500 ensayos generativos C++ con ocho propiedades.
- Benchmark: n=1.000/10.000/100.000/500.000, siete repeticiones, warm-up excluido del tiempo. Los tiempos incluyen asignación/copia/expansión/ordenación, no arranque ni lectura CLI.

## Artefactos y comandos individuales

- `src/main.cpp`: CLI modular para fixtures, benchmark y detalles de plataforma.
- `tests/test_weighted.cpp`: comprobaciones activas también en Release (no depende de assert/NDEBUG).
- `tests/test_oracle.py`: unittest del oráculo y rechazos CLI.
- `benchmarks/config.json`, `audit.py`, `coverage.py`: configuración, referencia racional, CSV y figura SVG.
- `results/accuracy.csv`, `fixtures.json`, `fixtures.txt`: inputs y comparación, con numerador/denominador exactos.
- `results/performance.csv`, `comparison.svg`: tiempo y memoria; `metadata.json`: hardware, plataforma numérica y hashes.
- `results/coverage.json`: cobertura de **líneas del header ponderado**, no del pipeline entero; raw gcov JSON comprimido conservado.
- `results/checks.json`, logs CTest/Python/lint/tipos: evidencia ejecutada.
- `informe.md`, `MVP.md`, `referencias.bib`: interpretación, alcance y referencias.

Después de instalar: `ctest --test-dir build/release --output-on-failure`; `python -m unittest discover -s tests -p 'test_*.py' -v`; `build/release/weighted_tail_cli --platform`; `python benchmarks/audit.py`.

## Sanitizers y memoria: alcance explícito

ASan y UBSan están habilitados. La detección de fugas local se desactiva por defecto (`detect_leaks=0`) porque LeakSanitizer no puede inspeccionar procesos en el entorno gestionado; el intento fallido se conserva en `results/initial-lsan-failure.txt`. **No se afirma verificación local de fugas**. En un entorno compatible ejecutar `ASAN_OPTIONS=detect_leaks=1 bash run.sh`; la CI usa esa opción. No hay concurrencia propia: TSan no se ejecutó.

RSS se mide dentro del ejecutable mediante Linux `/proc/self/status` (VmHWM), después de exec. Incluye dataset, runtime, warm-up y objetos temporales; no es memoria exclusiva del algoritmo. `wait4` se conserva como diagnóstico adicional porque puede heredar máximos del padre Python. La primera medición potencialmente engañosa se conserva en `results/initial-wait4-performance.csv` y no se usa para afirmar mejoras de memoria.

Prototipo de validación numérica: no modela PD/LGD/EAD, no calibra probabilidades, no pronostica riesgo ni calcula capital regulatorio.
