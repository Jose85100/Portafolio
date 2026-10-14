# ES ponderado C++: contrato numérico y benchmark equivalente

Ciclo de investigación: **2026-10-14**. MVP completo; resultados de la ejecución local documentada, no métricas inventadas ni una propuesta sin implementación.

## 1. Pregunta, hipótesis y novedad incremental

¿Puede una API C++ de ES ponderado reproducir el funcional exacto de una distribución finita, mantener contribuciones representables con pesos extremos y evitar la expansión de escenarios del baseline uniforme existente?

Hipótesis falsable H1: error escalado `abs(ES_cpp-ES_ref)/max(1,abs(ES_ref))` <=1e-12 y error relativo <=1e-12 para referencia no nula, en los fixtures fijados. H2 exploratoria: menor mediana de tiempo que expandir pesos enteros y ejecutar `quant::tail` para n>=10.000. No se afirma que sea más rápido para todo tamaño, arquitectura o distribución.

Novedad incremental del portafolio: API C++ integrada de pesos, fixtures compartidos Python/C++, referencia racional independiente y nuevo benchmark justo. No es una definición nueva de ES, ni un algoritmo de suma inventado aquí. No se afirma «nadie lo ha hecho».

## 2. Auditoría del repositorio y brecha

Base `c213a687d501faae8b2637546f89b980425adfad`. El PR #32 del aporte Python ya está integrado. Se revisaron README, CMake, tests y `include/quant/risk.hpp` de risk-engines, además del motor Python anterior. No se encontró AGENTS.md en el árbol ni un PR C++ ponderado equivalente en la búsqueda realizada.

`quant::tail` ya calcula ES con masa fraccionaria para probabilidades iguales. No se corrige ni sustituye. La brecha específica es admitir probabilidades desiguales y validar su contrato aritmético. Una segunda brecha detectada experimentalmente es la normalización prematura en binary64 del aporte Python con rangos de pesos extremos.

La nueva API está en `include/quant/weighted_tail.hpp`; el MVP ejecutable, tests, benchmark y evidencia en `weighted-tail-audit/`. No se modifican comportamientos de los tres motores originales. Su CTest de regresión en Debug pasó.

## 3. Estado del arte y fuentes

- Acerbi–Tasche (2002): coherencia de ES y problemas de expectativas condicionales con átomos.
- Rockafellar–Uryasev (2002): CVaR para distribuciones generales y representación mediante minimización hinge.
- Hyndman–Fan (1996): convenciones de cuantiles; no se equipara VaR inversa-CDF con interpolación.
- Higham (2002), NIST DLMF y Numerical Reproducibility: aritmética finita, estabilidad y dependencia de precisión/compilador.
- Bouchard–Reghai–Virrion (2021): cálculo de ES con detección eficiente en simulación anidada; problema distinto, por eso no se usa como benchmark de velocidad equivalente.
- LLVM: instrumentación ASan; no demuestra por sí sola ausencia de bugs.

Ocho entradas verificables en referencias.bib. Búsqueda focalizada en arXiv, SSRN, Semantic Scholar, Papers with Code, NIST, BIS, ECB y editoriales. Cobertura parcial, no revisión sistemática exhaustiva. Algunas aperturas arXiv/editoriales fallaron; se verificaron metadatos en resultados primarios y fuentes de autor, sin afirmar lectura del texto completo. Registro en benchmarks/prior-art.md.

## 4. Método y convenciones

Pérdidas finitas positivas/negativas; pesos finitos no negativos; alpha dentro de (0,1). Pesos cero se excluyen. Se escalan pesos por su máximo, se normalizan en `long double`, se ordenan pérdidas y se integra la masa 1-alpha con frontera fraccionaria. Sumas compensadas de Neumaier y escalamiento de pérdidas evitan productos o acumulaciones innecesariamente fuera de rango. Tiempo O(n log n), memoria O(n). Son técnicas conocidas.

VaR es la inversa izquierda de la CDF; el baseline viejo interpola el cuantil. Se compara **ES**, no se declara superioridad del pronóstico de VaR. Se rechazan entradas inválidas. No se admiten garantías para `-ffast-math`.

Oráculo: evaluar `t + sum(p_i max(L_i-t,0))/(1-alpha)` en cada átomo distinto y elegir el mínimo. Usa `Fraction` sobre el valor binario exacto de cada input float. No comparte el algoritmo de ordenación/integración ni normalización flotante con C++/Python. Referencia real racional, después redondeada a float para comparación con la salida double: coincidencia con ese redondeo **no implica exactitud aritmética ilimitada**.

## 5. Diseño experimental fijado

Config en benchmarks/config.json: seed=20261014; 200 distribuciones discretas generadas, n entre 2 y 32; pérdidas en décimas, positivas/negativas; pesos enteros 1–8; alpha=0.5/0.75/0.875/0.975/0.99. Siete casos diseñados adicionales: frontera, pérdidas negativas, peso cero, constante, valores grandes, cancelación firmada, probabilidad extremadamente pequeña. Total: 207 fixtures.

Benchmark n=1.000, 10.000, 100.000 y 500.000; siete repeticiones y tres modos; total 84 filas. Pérdidas y pesos generados en C++ mediante mt19937_64 y operaciones enteras explícitas. Mismas realizaciones/confianza para comparadores, sin simulación estocástica dentro del algoritmo de riesgo. No son datos de mercado ni modelos calibrados de un régimen financiero.

Baseline equivalente: repetir cada pérdida w_i veces y llamar al `quant::tail` real. Para pesos enteros es la misma distribución y el mismo ES. Se incluye el costo de expansión. Ablación: usar una copia por escenario e ignorar pesos; no es un competidor equivalente. El aporte Python se ejecuta realmente desde su archivo del repo; hashes guardados.

Hardware local: AMD EPYC 9V74, Linux x86-64/glibc 2.39, GCC/gcov 13.3.0, Python 3.12.14, NumPy 2.1.3. `long double`: 64 bits de significando y exponente máximo 16384; tamaños de escenario/átomo 16/32 bytes. No se interpreta como binary128. Flags Release estándar, sin fast-math. Herramientas fijadas en requirements.txt.

## 6. Implementación y reproducción

Header central reutilizable, CLI C++17 y CMake independiente; tests de invariantes con comprobaciones activas incluso en Release; harness Python tipado; oráculo racional; fuentes/fixtures/CSV/JSON/SVG/gcov. No se necesita notebook nuevo en esta ruta C++ (`src/` satisface la alternativa); no se inventan salidas de notebook.

Comando único desde la raíz del repo:

```bash
bash 04-quant-strategy-and-products/risk-engines/weighted-tail-audit/run.sh
```

Instala herramientas y ejecuta validaciones, sanitizers, cobertura y regresión. Linux/Python 3.12/g++/gcov/make; requiere red para instalación inicial y el repo completo para cargar el baseline Python. Los tiempos y memoria varían entre máquinas.

## 7. Tests y cobertura real

- 4.024 comprobaciones C++: casos analíticos/invalidaciones y 500 ensayos generativos con ocho propiedades: expansión equivalente, baseline uniforme, traslación, homogeneidad, monotonía, subaditividad con mismos pesos, escalamiento de pesos y permutación.
- Ocho unittest Python del oráculo y parsing/rechazo CLI pasaron; incluyen subcasos inválidos y probabilidad pequeña representable.
- CTest Release, Debug instrumentado ASan/UBSan, cobertura y regresión del motor anterior pasaron. La CLI instrumentada ejecutó los 207 fixtures y los tres modos de benchmark con n=1.000.
- GCC `-Wall -Wextra -Wpedantic -Werror`, Clang-Tidy, Clang-Format, Ruff y mypy pasaron para el código propio. Clang-Tidy no audita íntegramente bibliotecas del sistema; sus advertencias no-user se excluyen.
- Cobertura **de líneas del header ponderado: 60/62 = 96,77 %**. No es cobertura de todo el pipeline ni porcentaje de branches. Las dos guardas defensivas de underflow/overflow no se activaron en esta plataforma. Raw gcov JSON comprimido conservado.
- Generación property-based propia con semilla, sin shrinker automático; no equivale a una demostración formal.

## 8. Resultados numéricos ejecutados

Las **207 salidas ES C++ coinciden** con la referencia racional redondeada a double: error escalado y relativo máximos observados **0** en ese criterio. Esto valida H1 para el diseño, no para todos los inputs.

| Caso | ES de referencia redondeado | Python previo | C++ nuevo |
|---|---:|---:|---:|
| Pérdidas 0/100, pesos 99/1, alpha=.975 | 39.999999999999964 | igual | igual |
| Pérdidas 1e308/1e308, pesos 1e308/1e308 | 1e308 | 1e308 | 1e308 |
| Pérdidas 1e308/0, pesos 1e-300/1e300, alpha=.975 | 3.999999999999996e-291 | 0 | 3.999999999999996e-291 |

En el último caso, la razón de pesos es aproximadamente 1e-600: se pierde al dividir en binary64 antes de multiplicar por una pérdida grande. Precisión extendida conserva esa probabilidad y produce un ES final representable en double. El Python previo tiene error relativo del 100 % allí, aunque el error absoluto es ínfimo. Por eso una tolerancia exclusivamente absoluta habría ocultado la diferencia. **No se afirma relevancia económica de ese caso extremo ni mayor calidad de pronóstico.** No se modifica el baseline para que parezca mejor/peor.

## 9. Rendimiento y memoria observados

Valores del run local registrado; mediana de siete tiempos. ES ponderado y expansión comparan el mismo objetivo. Pico de RSS propio: máximo de VmHWM leído dentro del ejecutable, incluye dataset/runtime/warm-up/temporales; no es memoria exclusiva del algoritmo.

| Escenarios | Ponderado ms | Expandido ms | Razón expandido/ponderado | RSS ponderado KiB | RSS expandido KiB |
|---:|---:|---:|---:|---:|---:|
| 1.000 | 0.0455 | 0.0579 | 1.27 | 1.920 | 1.936 |
| 10.000 | 1.0772 | 2.1763 | 2.02 | 2.348 | 2.400 |
| 100.000 | 12.7796 | 26.4146 | 2.07 | 6.568 | 6.960 |
| 500.000 | 73.2788 | 149.2772 | 2.04 | 25.320 | 27.272 |

H2 exploratoria satisfecha en n>=10.000 en este run. No hay intervalos inferenciales ni control completo de carga de la máquina. Las siete repeticiones no son siete plataformas independientes. La memoria adicional evitada es modesta, no una mejora de órdenes de magnitud. Para 500.000 escenarios, la ablación uniforme tarda 41,585 ms y usa 13.600 KiB, pero ignora pesos y computa otra medida: se conserva como resultado negativo, no como derrota/victoria válida del objetivo ponderado.

Figura exacta de los CSV: results/comparison.svg. Eje de escenarios logarítmico. Los outputs crudos permiten comprobar cada número; no se reemplazan por métricas fabricadas.

## 10. Fallos, reparación de medición y límites

1. LeakSanitizer falló al inspeccionar `/proc/.../task` bajo las restricciones del entorno. El fallo inicial queda en results/initial-lsan-failure.txt. Se redujo alcance local a ASan+UBSan con detect_leaks=0, sin declarar verificación de fugas. CI habilita detect_leaks=1 en entorno compatible; su resultado debe verificarse aparte.
2. La primera medición wait4 dio máximos iguales condicionados por el padre Python; podía inducir una conclusión errónea sobre memoria. Se conserva en initial-wait4-performance.csv. La métrica usada ahora es VmHWM del proceso después de exec, y wait4 queda como diagnóstico adicional.
3. Clang-Tidy detectó parámetros enteros fácilmente intercambiables en funciones internas; se reemplazaron por BenchmarkConfig, sin silenciar ese check. Lint/formato/tipos iniciales se corrigieron antes del cierre.
4. No se implementó pybind11, estimación de probabilidades, calibración PD/LGD/EAD, pricing, stress regulatorio, backtesting temporal ni TSan. No hay concurrencia propia. Linux es el alcance probado; en plataformas donde long double=binary64, rangos extremos pueden rechazarse.
5. No se promete equivalencia bit a bit entre compiladores/arquitecturas ni exactitud universal. Un mal modelo/pesos puede dominar cualquier mejora aritmética. El oráculo de fracciones es caro y solo se usa en fixtures pequeños.
6. Pesos enteros 1–8 favorecen naturalmente al método que evita expansión; el baseline es correcto y útil, pero no representa todos los algoritmos ponderados de la literatura. No se compara contra un método avanzado de selección parcial porque ese sería otro experimento.

## 11. Rúbrica de autoevaluación (1–5)

| Dimensión | Puntaje | Motivo |
|---|---:|---|
| Novedad incremental | 3 | Extensión, contrato y benchmark del repo; métodos conocidos |
| Rigor | 4 | Oráculo exacto, propiedades y baseline equivalente; sin inferencia de rendimiento |
| Reproducibilidad | 5 | Un comando probado, seeds, inputs exactos, hashes y resultados crudos |
| Calidad de código | 4 | API tipada, lint, sanitizers y cobertura parcial; CLI sin bindings |
| Claridad | 4 | Diferencia definición, aritmética, pronóstico y memoria de proceso |
| Impacto potencial | 4 | Soporte de escenarios ponderados y prevención de silencios numéricos |
| Honestidad | 5 | Fallos, alcance y ablations negativas conservados |
| MVP completo/ejecutable | 5 | Código, pruebas, comparación numérica y artefactos reales |

## 12. Checklist y siguiente iteración

[x] src real; [x] comando único; [x] test automatizado pasado; [x] baseline con números; [x] CSV/JSON/figura; [x] README/informe/BibTeX/MVP; [x] carpeta correcta del repo. Publicación por rama y pull request, sin alterar main directamente.

Siguiente iteración recomendada: endurecer el contrato multiplataforma y transferir la corrección numérica al motor Python.

1. `03-financial-risk`: corregir o rechazar explícitamente rangos de pesos que produzcan underflow, con fixtures de esta auditoría y regresión del PR #32.
2. `04-quant-strategy-and-products/risk-engines`: ampliar CI GCC/Clang y política long double/binary64, con bindings Python opcionales y controles de fugas.
3. `03-financial-risk`: separar error aritmético, incertidumbre poblacional y backtesting ES fuera de muestra con pesos estimados.
