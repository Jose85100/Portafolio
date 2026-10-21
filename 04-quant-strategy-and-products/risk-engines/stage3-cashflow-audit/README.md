# Stage 3 cash-flow contract — C++17 MVP (2026-10-20)

Port verificable del núcleo Python ya existente: no es un nuevo modelo IFRS 9.
API pública en `../include/quant/stage3.hpp`, CLI en `src/main.cpp`, pruebas en
`tests/`, auditoría y oráculo independientes en `benchmarks/audit.py`.
No cambia los motores actuales de default, mercado o liquidez.

## Un comando desde la raíz del repositorio

```bash
bash 04-quant-strategy-and-products/risk-engines/stage3-cashflow-audit/run.sh
```

Entorno reproducible: Linux x86_64, Python 3.12 con venv/pip, GCC/g++ y gcov
compatibles (local: 13.3.0). Hace falta internet inicial para instalar las 18
versiones fijadas de requirements.txt; CMake y herramientas LLVM se instalan en
el venv. No se necesitan Eigen, bindings ni GoogleTest: este contrato pequeño
usa STL y un ejecutable de pruebas con CTest. No se fija imagen de SO ni hashes
de wheels; no se promete identidad binaria entre plataformas.

El comando ejecuta Ruff, formato, mypy del benchmark, clang-format, clang-tidy,
CMake/CTest, compilación con warnings como errores, ASan/UBSan, gcov, 288
fixtures contra Decimal y Python, y 42 mediciones de tiempo/RSS. Guarda CSV,
JSON y PNG/SVG en results/. Los binarios y venv no se publican.
El CLI sólo recibe fixtures numéricas internas; no es un parser financiero
hostil hardened. `build/stage3_cli --fixtures results/fixtures.txt` produce CSV.

ASan local tiene detección de fugas desactivada por defecto por restricciones de
entornos administrados; no se afirma verificación local de fugas. CI fija
`ASAN_OPTIONS=detect_leaks=1`. Para activarla localmente:
`ASAN_OPTIONS=detect_leaks=1 bash run.sh` desde esta carpeta.

## Contrato y fundamento

Activo ya deteriorado, no POCI; G es importe bruto al cierre y C recuperaciones
netas esperadas, no LGD ya descontada. Una EIR original fija, años desde cierre,
sin nueva PD de primer default. Se admiten G, C, tiempos y tasa finitos y no
negativos; vector no vacío, dimensiones iguales, suma nominal de C <= G.
Se rechazan tasas negativas y surplus deliberadamente, aunque el motor general
Python tenga otras rutas. La API no determina stage ni estima recuperaciones.

Para este dominio:

`loss = (G - sum(C)) + sum(C * -expm1(-log1p(r) * t))`.

Evita cancelación de `G - PV` en el caso de recuperación completa y tasa diminuta.
No utiliza long double ni fast-math. La suma de muchos flujos sigue redondeando:
no es un guard universal contra underflow ni un contrato de céntimos exactos.

## Evidencia y mantenimiento

- `results/accuracy.csv`: inputs, Decimal100, Python real, C++ y ablación.
- `results/fixtures.txt`: mismos inputs binary64 para ambos lenguajes; hash en JSON.
- `results/performance.csv`: 42 muestras con checksum, VmHWM del CLI y RSS wait4.
- `results/coverage.txt`: cobertura gcov, distinguir núcleo de STL y CLI.
- `results/summary.json`: métricas ejecutadas, versiones, CPU y hash del modelo Python.
- `informe.md`: prior art, resultados negativos y límites.
- `referencias.bib`: siete referencias reales.

La comparación de paridad carga el módulo real de 03-financial-risk del mismo
checkout, no una reimplementación escondida. El hash se registra para detectar
cambios, no se bloquea su evolución. La CI se activa también si cambia ese módulo.
Los resultados guardados son una corrida local; `run.sh` los regenera.
VmHWM se lee dentro del CLI tras exec; wait4 puede incluir el pico heredado del
Python previo al exec. Se guardan ambos para no confundir ese artefacto con el
uso de memoria del cálculo. No son mediciones de asignaciones incrementales.

![Precisión y coste](results/comparison.png)

Checklist MVP: código src y header, comando único, tests, baseline numérico,
CSV/JSON/figura, documentación y carpeta risk-engines: completos.
