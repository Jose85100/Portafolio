# Auditoría de ES ponderado — ciclo 2026-10-13

## 1. Pregunta e hipótesis

¿Las convenciones de cola del portafolio producen el ES de la misma distribución finita cuando hay átomos, fronteras fraccionarias o pesos desiguales?

H1 operacional: máximo error absoluto contra el LP <=1e-8 en 320 distribuciones con alpha=0.975. Métrica: error numérico sobre la distribución finita, no error de pronóstico. No se usa Kupiec ni un test ES fuera de muestra: no hay forecasts temporales que permitan interpretarlos.

## 2. Auditoría y brecha

Commit base: `db51d4def262980c002e9be799b7e3cd034108f9`. Sin AGENTS.md encontrado en el árbol. Estructura y baselines revisados: README de riesgo, VaR/ES histórico, laboratorio de liquidez, `risk_models.py` de construcción y `quant/risk.hpp` C++.

- `historico` promedia retornos bajo un cuantil interpolado. Con masa en la frontera puede incorporar más que la cola requerida.
- `empirical_var_es` de construcción incluye íntegramente el estadístico frontera por posición; puede exceder la masa de cola.
- `tail_risk` de liquidez y `quant::tail` C++ **ya usan ES fraccionario uniforme**. No se afirma haber inventado ni corregido esa lógica.
- No encontré soporte de probabilidades desiguales en las funciones auditadas; esto no prueba su ausencia en todo el repo o literatura.

El MVP agrega un motor ponderado independiente y una auditoría que ejecuta tres funciones reales del repo mediante AST, sin sus demos. Se conservan rutas y SHA256 en metadata. No modifica comportamientos existentes ni añade C++ nuevo.

## 3. Prior art y novedad incremental

Artzner et al. (1999) formalizan coherencia. Acerbi–Tasche (2002) distinguen ES de expectativas condicionales de cola en distribuciones discontinuas. Rockafellar–Uryasev (2002) desarrollan CVaR para distribuciones generales. Hyndman–Fan (1996) describen convenciones de cuantiles. Acerbi–Tasche, Economic Notes (2002), aportan representaciones y estimación de ES. BIS (2019) contextualiza ES en riesgo de mercado; no valida este MVP regulatoriamente.

Referencias verificadas el 2026-10-13 vía arXiv, páginas de autores, editoriales y BIS. La apertura del texto editorial de Rockafellar–Uryasev falló; título/DOI se verificaron en resultados editoriales y universitarios. Consulta adicional SSRN, Semantic Scholar, ECB WP y Papers with Code: cobertura de búsqueda parcial, sin revisión sistemática exhaustiva. No se afirma «nadie lo ha hecho». Detalle en benchmarks/prior-art.md; seis referencias BibTeX en referencias.bib.

Novedad incremental: nuevo benchmark del portafolio, extensión a escenarios ponderados, contrato de masa de cola y comprobación con oráculo LP. **No es una fórmula ni teoría nuevas.**

## 4. Método y validación numérica

Pérdidas positivas o negativas finitas; pesos no negativos, normalizados, con escenarios de peso cero excluidos. VaR es la inversa izquierda de la CDF. ES integra exactamente la masa 1-alpha, partiendo el átomo frontera.

Ordenando pérdidas descendentes, se usa u_i=min(p_i, max(1-alpha-sum(j<i)p_j,0)); ES=sum(u_i L_i)/(1-alpha). Complejidad O(n log n), memoria O(n). Se escalan pesos y pérdidas para disminuir riesgo de overflow y se usa math.fsum para la suma final.

Oráculo: max sum(q_i L_i), sujeto a sum(q_i)=1 y 0<=q_i<=p_i/(1-alpha), resuelto por SciPy HiGHS. Implementación del optimizador independiente del algoritmo de ordenación, pero comparte validación/normalización; los casos analíticos protegen contra errores compartidos. No es prueba formal de la implementación.

## 5. Diseño fijado

Config: alpha=0.975; n=250 y 501; 40 réplicas por distribución; seed base=20261013, seed efectivo=base+replica+10000*n. Normal IID N(0,1); Student t4 dividido por sqrt(2); crédito binario IID PD=0.01, severidad=100; t4 redondeada a 0.1 con pesos lognormales sigma=1.5 independientes de la pérdida. Son distribuciones de escenarios, no series temporales ni calibración de mercado. La independencia y estacionariedad sintética no modelan contagio ni cambios de régimen.

320 distribuciones × cinco métodos = 1.600 filas en trials.csv. Se comparan métodos sobre las mismas realizaciones y confianza. Los métodos uniformes en escenarios ponderados son **ablaciones de pesos**, no competidores ponderados válidos. El LP es el competidor ponderado.

Hardware: model name	: AMD EPYC 9V74 80-Core Processor; Linux x86_64; Python 3.12.14; NumPy 2.1.3, SciPy 1.14.1. Hilos BLAS/OMP fijados a uno. Dependencias completas fijadas en requirements.lock.txt.

## 6. Resultados reales

Máximo error absoluto ES ponderado vs LP: **7.105427357601002e-15**, por debajo de 1e-8. Hipótesis operacional satisfecha en el diseño ejecutado.

| Distribución | Histórico MAE | Construcción MAE | Liquidez MAE | Ponderado MAE |
|---|---:|---:|---:|---:|
| normal | 0.0271237 | 0.0271237 | 4.08007e-16 | 6.77236e-16 |
| student4 | 0.0595276 | 0.0595276 | 3.66374e-16 | 7.02216e-16 |
| discrete_credit | 35.4507 | 2.47232 | 5.75096e-15 | 1.06581e-15 |
| weighted_rounded_t | 0.662312 | 0.678885 | 0.711845 | 2.94209e-16 |


MAE calculado sobre 80 distribuciones por fila; unidades arbitrarias de pérdida. La última fila cambia al omitir probabilidades: no implica superioridad del modelo estadístico.

Contraejemplo exacto: 99 ceros + una pérdida de 100, alpha=0.975.

| Método | ES | Error frente a 40 |
|---|---:|---:|
| Histórico del repo | 1 | -97.5% |
| Construcción del repo | 33.333333 | -16.6667% |
| Liquidez fraccionaria del repo | 40 | 0% |
| Cola estricta (ablación) | 100 | +150% |
| Ponderado / LP | 40 | 0% |

Interpretación: 1% de probabilidad con pérdida 100 dentro de una cola de 2.5%; ES=100*0.01/0.025=40. Incorporar todos los ceros de frontera equivale a otra medida. Es un contraejemplo conocido en esencia, reproducido sobre código real del repo.

## 7. Tests y controles

**22 tests pasaron**, incluyendo cuatro propiedades con 100 ejemplos cada una: acuerdo con LP y referencia; traslación, homogeneidad y monotonía; subaditividad ponderada; acuerdo con baseline real de liquidez. Casos límite: pérdidas constantes/singleton/negativas, peso cero, entradas vacías/NaN/inf, alpha inválido y próximo a uno, pesos de 1e308, pérdidas de 1e300, fallo explícito del LP.

Cobertura de statements+branches del núcleo `src.tail` + `src.oracle`: **96.05%**; no representa cobertura del pipeline ni todos los módulos. La guarda de overflow de ES y una rama casi alpha=0 no quedaron totalmente cubiertas. Ruff lint/formato y mypy pasaron. No aplica sanitizers C++ porque no se modificó código C++.

## 8. Rendimiento, memoria y estabilidad

Warm-up excluido, siete repeticiones por método/tamaño, 98 observaciones. Tiempo separado de la medición de memoria. Mediana de ms; memoria máxima capturada por tracemalloc de asignaciones Python/NumPy. **No es RSS ni memoria nativa completa de HiGHS**.

| n | ES ponderado: ms | LP ponderado: ms | Referencia uniforme: ms | Histórico: ms | Pico ponderado: MiB |
|---:|---:|---:|---:|---:|---:|
| 250 | 0.0763 | 0.7080 | 0.0294 | 0.0505 | 0.028 |
| 2,500 | 0.4099 | 4.6168 | 0.1414 | 0.0670 | 0.268 |
| 25,000 | 3.9441 | No medido | 1.2884 | 0.4365 | 2.672 |
| 250,000 | 39.0014 | No medido | 13.7151 | 2.0691 | 26.704 |


Los algoritmos uniformes de la tabla computan otro objetivo en escenarios con pesos; sus tiempos describen el costo, no una victoria contra un competidor equivalente. LP y motor ponderado sí usan el mismo objetivo. La ventaja numérica frente a baselines por umbral tiene un costo de tiempo y memoria. No se afirma mejora de velocidad frente al histórico. Figura revisada: results/audit.png.

## 9. Fallos y ablaciones negativas

- Cola estricta devuelve NaN en **6 de 80** distribuciones de crédito (sin observaciones estrictamente por encima del cuantil). Se mantienen esas filas, sin reemplazar ni ocultar NaN; summary.csv declara inválidos, MAE válido excluye explícitamente esos casos.
- La referencia fraccionaria uniforme ya acierta sobre distribuciones uniformes. No hay mejora defendible allí.
- Al ignorar pesos, incluso el baseline uniforme correcto cambia el ES del objetivo ponderado.
- El método ponderado es más lento y usa más memoria que el promedio histórico en esta máquina.
- Arranque de notebook por kernel Jupyter TCP/IPC bloqueado por restricciones de sockets. Se cerró el entregable ejecutando las celdas con IPython en el proceso, capturando stdout y display_data reales. No se simularon outputs. run.sh usa esa ruta por defecto; se requiere Bash/Linux/macOS, no se validó Windows.
- Errores iniciales de lint/tipos se corrigieron antes del cierre; la última ejecución completa de un comando pasó.

## 10. Limitaciones y riesgo de modelo

Solo validación numérica de distribuciones finitas sintéticas. No prueba estimación insesgada del ES poblacional, elicitabilidad, eficiencia estadística ni calidad de pronósticos; no se ejecuta backtesting Acerbi–Szekely ni test Diebold–Mariano. Ponderación conocida, no estimada: mal calibrarla puede dominar cualquier mejora numérica. No incluye riesgo de liquidez, horizons, stress regulatorio, colas EVT ni capital IFRS 9/SFC/FRTB. Flotantes extremos con pesos de rangos muy desiguales pueden perder masa por underflow; no se garantiza exactitud arbitraria. El LP tiene tolerancias y comparte preprocessing. Tiempos no extrapolables automáticamente a producción. Baselines se cargan desde el repo: cambios futuros requieren revisar la auditoría y sus expectativas.

## 11. Reproducción y entrega

Desde esta carpeta: `bash run.sh`. Se instala y ejecuta todo; requiere Python 3.12 y red inicialmente. Resultado verificable: tests, JSON, CSV, PNG y notebook con tres celdas de código ejecutadas. No necesita datos privados. README.md, MVP.md, src/, tests/, benchmarks/, results/, referencias.bib, requirements y workflow CI acompañan el MVP.

## 12. Rúbrica (1–5)

| Dimensión | Puntaje | Justificación |
|---|---:|---|
| Novedad incremental | 3 | Extensión/auditoría del repo; fórmula conocida |
| Rigor | 4 | Oráculo, analíticos y propiedades; sin inferencia poblacional |
| Reproducibilidad | 5 | Un comando ejecutado, lock, seeds, hashes, notebook |
| Código | 4 | Modular/tipado/lint; captura notebook dinámica, cobertura parcial |
| Claridad | 4 | Distingue definición, estimación y predicción |
| Impacto potencial | 4 | Convenciones de cola pueden afectar decisiones sobre escenarios discretos |
| Honestidad | 5 | Fallos, alcance y comparadores válidos explicitados |
| MVP ejecutable completo | 5 | Artefactos, output y pruebas reales |

## 13. Checklist

[x] src/ real; [x] comando único; [x] tests pasados; [x] baseline con números; [x] outputs; [x] README/informe/BibTeX/MVP; [x] ubicación correcta del repo.

## 14. Siguiente iteración

Siguiente iteración recomendada: armonizar convenciones sin perder trazabilidad de resultados históricos.

1. `03-financial-risk`: proponer migración de ejemplos históricos/construcción a masa fraccionaria con pruebas de regresión y documentación del cambio de resultados.
2. `04-quant-strategy-and-products/risk-engines`: extender el motor a pesos y fixtures comunes Python/C++, con ASan/UBSan y ctest.
3. `03-financial-risk`: añadir simulación de estimación poblacional y backtesting ES fuera de muestra, separando error numérico e incertidumbre estadística.
