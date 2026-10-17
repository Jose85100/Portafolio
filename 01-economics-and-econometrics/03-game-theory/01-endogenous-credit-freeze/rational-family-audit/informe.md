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
no es bienestar social. Sin datos reales, estimación estructural, identificación causal,
selección de equilibrio ni probabilidades empíricas de congelación.

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
son prueba formal ni validación S3. No hay datos reales, estimación causal, selección,
política óptima ni métricas de bienestar social. No generalizar resultados a sistemas
bancarios ni a más tipos/agentes. La independencia de implementación no implica
independencia de todos los primitives reutilizados: modelo/exportador son compartidos.
