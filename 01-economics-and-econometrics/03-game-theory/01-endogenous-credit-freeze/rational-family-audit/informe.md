# Informe crítico — Rational Family Audit (2026-10-17)

## Revisión y brecha local

Base main revisada: `b19c03599a1f7cbb88a17eaed65fdd590dbb009a`. Se inspeccionaron
commits recientes, README de dominio/programa, RESEARCH_STANDARDS, fuentes de los
cuatro MVP anteriores y workflows. No se encontraron AGENTS.md. Los PR #33/#37/#40
cubren puros/mixtos aislados/familias; #43 ejecutó Nashpy, pero dejó pendiente Gambit
y su parser. #44/#45 son aportes concurrentes de otras áreas y no se modifican.
Estado actual verificado:12 programas,10 S1 y dos con componentes S2; no se reutiliza
el estado inicial de12 S1 como vigente.

Este MVP cierra la ejecución del parser real y solver racional externo. Reconstruye
localmente familias de comportamiento desde sus extremos, con algoritmo distinto
al baseline de restricciones afines. Es novedad incremental **del repositorio**, no
prioridad científica: enumeración extrema y grafos de compatibilidad son conocidos.

## Pregunta, hipótesis y umbral

¿Se reconstruyen las mismas familias máximas por inclusión que el baseline racional
del repo? H1: igualdad **exacta**, sin tolerancias, de ambos factores convexos de cada
familia en los cuatro casos canónicos y nueve adicionales; cero discrepancias y
regret interino racional cero en las muestras. Aserciones ejecutables fallan ante
cualquier desacuerdo. No se certifica un solver genérico ni un teorema nuevo.

## Modelo, identificación y datos

Dos prestamistas, theta binario con prior interior pi; señales privadas binarias,
independientes dado theta, precisión q. u_i=a_i(theta+alpha*a_j-c), agentes neutrales
al riesgo, parámetros comunes conocidos y mezclas independientes entre jugadores.
No restricciones de balance, colateral ni prestatarios explícitos. Payoff de prestamista
no es bienestar social. El estudio utiliza juegos simulados; la estimación estructural, identificación causal,
selección de equilibrio y probabilidades empíricas de congelación requieren investigación posterior.

Matrices ex ante obtenidas por suma sobre ocho estados, con Fraction(str(parámetros)).
Se representan decimales racionales exactos, no incertidumbre económica. Cuatro planes
contingentes por jugador, orden00/01/10/11. El parser real Gambit comprueba **32 payoffs**
contra las matrices racionales antes de invocar enummixed_solve(rational=True).

## Métodos y dependencia de completitud

El exportador del ciclo anterior se reutiliza sin modificar. Gambit16.4.1 enumera
extremos estratégicos racionales. Proyección a marginales por tipo; esas marginales,
no la correlación entre acciones contrafactuales de tipos mutuamente excluyentes,
determinan los payoffs. El código nuevo forma un grafo bipartito de compatibilidad:
una arista exige regret ex ante racional cero del par de marginales, calculado
con matrices directas y lift independiente. Con tipos de probabilidad positiva,
cero regret ex ante implica cero interino; esta equivalencia **exacta** no justifica
un filtro aproximado uniforme para tipos raros (control negativo del ciclo anterior).

Se enumeran bicliques mediante intersección de vecindarios/cierre y se construye
producto(conv(izquierda),conv(derecha)). Hull2D usa aritmética racional y algoritmo
monotone-chain; se quitan puntos colineales e interiores y productos contenidos.
No se llama al hull ni a gains del baseline para reconstruir. La verificación final
sí compara con sus factores racionales, y las muestras se verifican con exact_regret
del baseline. El algoritmo es exponencial y **rechaza más de12 marginales por lado**.
Depende de recibir los extremos externos necesarios; input vacío/inválido se rechaza,
pero un input incompleto no se transforma mágicamente en un certificado de completitud.

No se ejecutó lrs ni Gambit CLI -c; la reconstrucción de familias es local. Tampoco
se afirma que las familias máximas sean componentes conexas o una partición disjunta.

## Diseño y ejecución

13 configuraciones: regular(.5,.8,.9,.8); coordinación con q=.5; indiferencia total
q=.5,c=.5,alpha=0; singular aislado q=1,c=1; perturbación q=.500000001; ocho juegos
racionales generados con seed20261017:pi∈{.2,...,.8},q∈{.5,...,1},c∈{.1,...,1.2},
alpha=.8. config.json guarda cada valor. Diez combinaciones convexas racionales por
familia;380 muestras guardadas. Lotes1/2/4 por método y escenario miden throughput
de juegos4x4, no crecimiento en jugadores/tipos. Tiempo incluye exportación, parser,
solver y reconstrucción; excluye instalación. tracemalloc mide sólo asignaciones
Python, **no memoria del solver C++ ni RSS**, por lo que no se declara superioridad
global en memoria. Los lotes retienen outputs durante la medida.

Entorno ejecutado:Linux x86_64, Python3.12.14, GCC13.3.0, AMD EPYC9V74,9 CPUs virtuales
visibles. Ejecución secuencial, sin afinidad ni control de threads BLAS. Dependencias
directas fijadas; environment-lock registra transitivas. Build aislado de PyGambit
no es una garantía de reproducibilidad binaria bit-a-bit entre toolchains.

## Resultados reales

| Caso | Perfiles externos | Familias baseline / reconstruidas | Dimensión máxima | Coincidencia exacta |
|---|---:|---:|---:|---|
| Regular |5|5 /5|0|Sí|
| Coordinación |11|3 /3|2|Sí|
| Indiferencia total |16|1 /1|4|Sí|
| Singular aislado |2|2 /2|0|Sí|
| Cerca de degeneración |5|5 /5|0|Sí|

**13/13 configuraciones coinciden** en los factores completos, no sólo en número de
vértices o dimensión. Las380 muestras tienen regret interino exactamente0. El caso
q=.5 tiene familia2D y dos puntos; q=.500000001 tiene cinco puntos aislados. Exactitud
aritmética no elimina fragilidad paramétrica ni valida una calibración económica.

Caso regular, medida inicial bajo tracemalloc: externo+reconstrucción~0.0261s frente
a~0.0637s baseline; picos Python19468 frente167771 bytes. Es una observación pequeña,
sin intervalo de confianza ni claim de speedup general. Comparación completa por lote
y todos los casos en timing.csv; no comparar esta memoria como si incluyera C++.

Tests: **10 nuevos** con72 ejemplos Hypothesis deterministas (12 juegos,60 hulls),
edge cases, negativos y fallos explícitos; **51 regresiones** (9 strategic,10 polyhedral,
12 mixed,12 pure,8 comunes), **61 tests pasan**. Cobertura nueva src:86 statements,
32 branches, **100% líneas y ramas**. No mide scripts benchmark ni código externo.
Ruff y mypy de src pasan. Se ejecutó también desde raíz el comando común solicitado:
`python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v`.

## Controles negativos y fallos

1. Convexificar todos los equilibrios regulares introduce el punto(.5,.5,.5,.5),
   con regret ex ante **3/20=.15**: no es equilibrio. En coordinación/indiferencia
   el mismo punto sí tiene regret0, controles que evitan generalizar indebidamente.
2. Conservar un solo perfil devuelve dimensión0 y pierde las familias2D/4D. En
   regular también omite otros puntos aislados aunque no cambie dimensión máxima.
3. Input vacío, probabilidades inválidas, perfil no-equilibrio y cap de búsqueda
   se rechazan. Tests mutan payoff externo o dimensiones y exigen fallo del contrato.
4. Instalación inicial falló por clang++ ausente; segundo intento por ruta llvm-ar
   inexistente. Se resolvió con CC/CXX/AR/RANLIB/LDSHARED GNU explícitos; la compilación
   e instalación finalmente se ejecutaron. El primer adaptador usó índices enteros
   para Outcome; la API16.4.1 exige objetos Player. Se corrigió y rerun completo pasó.
   No se ocultan esos fallos como ausencia de equilibrios o validación pendiente.

## Prior art y cobertura (2026-10-17)

Revisión parcial por buscador, no sistemática. Se leyeron documentación primaria y
fichas/resúmenes; no se presume lectura integral o reproducción de cada artículo.

| Canal / consulta | Cobertura y límites |
|---|---|
| Gambit16.4.1 enummixed, API, NFG | Racionales y extremos; CLI-c documenta conjuntos convexos. API racional ejecutada; CLI-c no ejecutada. |
| Autor: rahulsavani/bimatrix_solver README | Enumera extremos con lrs y cliques máximos para componentes. Antecedente directo, no se ejecutó su implementación ni se copió código. |
| SIAM Audet2001 | DOI10.1137/S1064827598339086; ficha/resumen sobre enumeración extrema y uniones de poliedros. |
| INFORMS Harsanyi1967 | DOI10.1287/mnsc.14.3.159; fundamento bayesiano, no algoritmo nuevo. |
| SSRN Avis1365927 | Ficha/resumen recuperados; descarga indica no disponible. No se afirma lectura integral. |
| NBER22297 | Angeletos/Lian2016, coordinación con información incompleta; motivación, no benchmark comparable. |
| CEPR DP3233 | Rochet/Vives2002, modelo bancario más rico y unicidad bajo sus supuestos. No transferir su unicidad a este juego. |
| arXiv econ.EM | Canen/Song2010.08868v7, resumen: contrafactuales dependen de invariancia de selección. No se estimó su modelo. |
| arXiv math.OC | Sagratella1512.00653, resumen: estrategias discretas, alcance diferente al conjunto mixto conductual. No se ejecutó su algoritmo. |
| arXiv q-fin.EC | Pangallo et al.1701.09043, ficha primaria: aprendizaje2x2, no solver comparable de familias4x4. |
| arXiv econ.TH/stat.ME | Consultas específicas y combinadas Nash/equilibrium enumeration: no candidato directamente comparable validado. No inferir inexistencia. |
| Semantic Scholar título Avis | No ficha primaria verificable recuperada; coincidencias externas/indirectas. |
| Papers with Code Nash enumeration Gambit | Stratego/Boolean Observation Games, no benchmark equivalente identificado. |
| Econometrica/JET/GEB maximal Nash subsets | Resultado primario McLennan2005 y referencias de recuentos genéricos, no benchmark ejecutado. AER/QJE/JPE/ReStud/JoE no revisados individualmente en este ciclo. |

referencias.bib contiene10 entradas reales. No se reclama prioridad de grafos,
bicliques, hulls ni enumeración racional. El aporte es un contrato auditable y
evidencia incremental reproducible en este programa finito.

## Artefactos, madurez y límites

README/reproduce.sh, src/tests, rawCSV/JSON/NFG y hashes, figura, notebook ejecutado
con outputs reales, requisitos/lock y MVP.md. Notebook ejecutado de arriba abajo
con IPython en proceso y nbformat validado; no se simuló ejecución de kernel externo.
La guía de notebooks/visualización orientó la estructura, captura de outputs y figura;
sus referencias compartidas no fueron accesibles. Visualización: revisión del PNG;
no se afirma QA interactivo o de viewport estrecho.

**S2 del componente; programa S2 parcial, continuo/empírico S1**. Trece escenarios no
son prueba formal ni validación S3. El estudio utiliza juegos simulados; la estimación causal, selección,
política óptima y métricas de bienestar social quedan fuera de esta entrega. No generalizar resultados a sistemas
bancarios ni a más tipos/agentes. La independencia de implementación no implica
independencia de todos los primitives reutilizados: modelo/exportador son compartidos.

## Extensión 2026-11-04 — sensibilidad del equilibrio a error de pagos

### Pregunta, brecha y candidatas

El MVP anterior certifica regret racional exactamente cero en el juego declarado, pero esa igualdad puede ser frágil al redondeo/calibración de utilidades. Se compararon: (i) cota exacta de regret bajo errores de caja por celda (elegida; implementable y falsable con enumeración de vértices), (ii) perturbación del prior privado (pospuesta porque requiere recalcular todas las matrices Bayesianas y discutir información), y (iii) variación del set de acciones/señales (pospuesta por ser cambio del juego, no sensibilidad de la solución).

### Fórmula, hipótesis y propiedades

Para pagos de jugador $A_{ij}$, estrategia propia $p_i$, estrategia rival $q_j$, y desviación pura $a$, regret nominal es $g_a=\sum_jq_j[A_{aj}-\sum_ip_iA_{ij}]$. Si cada entrada admite error independiente $\epsilon_{ij}\in[-\delta,\delta]$, el error máximo en la diferencia esperada es la función soporte de la caja: $\delta\sum_{ij}q_j|\mathbf1(i=a)-p_i|$. Por tanto $\epsilon$-regret robusto es $R_\delta=\max(0,\max_a[g_a+\delta\sum_{ij}q_j|\mathbf1(i=a)-p_i|])$. Es exacto para incertidumbre rectangular e independiente por celda; sería sólo cota conservadora si errores compartidos/correlacionados. El perfil sigue siendo mezcla conductual; no se modifica el equilibrio ni el payoff medio.

H1: el cálculo analítico coincide, a tolerancia 1e-12, con enumerar las 2^4 esquinas de la caja en 60 matrices diseñadas con semilla 4. La afirmación queda falsada por cualquier discrepancia. La utilidad es un certificado de fragilidad, no una predicción de probabilidad del error.

### Experimento y resultado

Juego de coordinación sintético con pagos [[1,-1],[-1,1]], estrategia mixta (1/2,1/2) por jugador. Baseline nominal: regret 0. Para deltas 0,.005,.01,.02,.05,.1, la cota exacta es igual a delta. Se comparó cada caso aleatorio con el oráculo de 16 vértices; 60/60 coincidieron. Cuatro tests locales cubren caso exacto, límite cero, caja y entradas inválidas. El generador guardó seis filas CSV, JSON y figura; tiempo total observado 104547 ns en una llamada de corrida y no constituye benchmark de rendimiento. La figura muestra unidades de utilidad; no representa muestra empírica.

### Interpretación, negativo y límites

El resultado muestra que un equilibrio exacto puede perder certificación con perturbaciones de pagos arbitrariamente pequeñas: no significa que el comportamiento económico cambie ni que la cota sea probabilística. Sin estructura de covarianza, el peor caso rectangular puede ser deliberadamente conservador. La extensión es adaptación de ingeniería/auditoría (no una novedad científica); conecta el regret racional exacto del solver con incertidumbre de calibración. Se conserva el resultado negativo de que certificación nominal cero no implica robustez positiva.

### Artefactos/reproducción/madurez

Desde la carpeta del programa: `python -m unittest tests.test_epsilon_robustness -v && python -m src.run_robustness`. El comando acumulativo `bash reproduce.sh` ahora incluye ambos. Código tipado: `src/epsilon_robustness.py`; tests contra todas las esquinas: `tests/test_epsilon_robustness.py`; configuración reproducible dentro de `src/run_robustness.py`; salidas bajo `results/payoff-uncertainty.*`; notebook suplementario `notebook_robustness.ipynb`. Referencias y matriz de prior art existentes en `referencias.bib` e `informe.md` (Gambit, Harsanyi, resultados de Nash y racionalidad); no se agregan afirmaciones regulatorias.

**Madurez:** componente local mantiene S2; extensión experimental adicional, no promoción de programa. S3 pendiente: incertidumbre estructurada correlacionada/paramétrica, más juegos y validación del DGP. Dataset diseñado sin licencia externa; semilla 4 en test, 20261104 en config; Python 3.12.14; Linux x86_64. Fórmulas y reporte describen incertidumbre sobre utilidad en unidades adimensionales.
