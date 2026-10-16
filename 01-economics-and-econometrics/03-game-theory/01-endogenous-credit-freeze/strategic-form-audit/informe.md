# Informe crítico — Strategic Form Audit, 2026-10-16

## 1. Revisión del repositorio y decisión

Base revisada: `681836e7c4be3108e4a4bad6e20dc9b0239808ab`, main del 16 de octubre.
Se inspeccionaron log reciente, README del dominio/programa, RESEARCH_STANDARDS.md,
fuentes y contratos de pure/mixed/polyhedral y workflows. No se encontraron AGENTS.md.
Los PR #33, #37 y #40 ya cubren puros, mixtos aislados y familias poliédricas; no se
duplica ese solver. Cambios recientes #36/#39/#41/#42 pertenecen a otras áreas y se
preservan. Estado verificado: 12 programas, 10 S1 y dos con componentes S2, no 12 S1.
Se amplía un componente S2 existente sin declarar S3 del programa entero.

## 2. Pregunta, brecha e hipótesis

Faltaba en este programa una ejecución de solver externo a partir de la forma
estratégica ex ante. No faltaban ni la transformación teórica ni algoritmos publicados.
H1: caso regular (.5,.8,.9,.8), cinco puntos racionales: Nashpy vertex enumeration
recupera los cinco tras proyección con distancia sup ≤1e-8 y regret interino <1e-8.
Ambos umbrales se verifican mediante aserción; para degenerados sólo se diagnostica,
sin atribuir completitud a una lista finita. Novedad incremental **local al repositorio**:
contrato de exportación exacta, contraste externo y falsación del chequeo ex ante solo.

## 3. Diseño y supuestos

Mismo modelo: theta binario, prior pi interior, dos señales binarias condicionalmente
independientes con precisión q≥.5; u_i=a_i(theta+alpha*a_j-c). Jugadores neutrales al
riesgo, parámetros comunes conocidos, mezclas independientes entre jugadores. Sin
presupuesto, riesgo sistémico dinámico ni borrower welfare. No hay datos observados,
estimando causal, identificación ni selección de equilibrio. Payoffs sintéticos exactos
con Fraction(str(param)); esto representa decimales, no incertidumbre paramétrica.

Cuatro planes contingentes por jugador. A/B se calculan sumando theta,s0,s1, no usando
las fórmulas afines de gains del baseline. Se exporta .nfg con racionales y se relee
con parser propio restringido antes de invocar Nashpy 0.0.43. La documentación de
Gambit verifica el orden; **Gambit no fue instalado/ejecutado** y su parser queda pendiente.
Proyección x_s=sum_plan w_plan a_plan(s); lift por producto Bernoulli. La proyección
no es inyectiva: correlaciones entre acciones de tipos mutuamente excluyentes no
identifican otra conducta observable. Las equivalencias aquí no son un nuevo teorema.

Cuatro escenarios canónicos en config.json, ocho sorteos seed 20261016: pi∈[.2,.8],
q∈[.55,.95], c∈[.3,1.2], alpha=.8. Dos métodos externos; sensibilidad de comparación
1e-12/1e-10/1e-8/1e-6; lotes 1/2/4 por método y escenario. Estos lotes miden throughput,
no crecimiento de dimensión ni complejidad asintótica. Sin intervalos inferenciales
ni claims de significancia para timings. No se perturban payoffs para borrar degeneración.

## 4. Evidencia ejecutada

| Caso | Baseline: vértices / dimensión máxima | Nashpy vertex: recuperados | Nashpy support: recuperados |
|---|---:|---:|---:|
| Regular | 5 / 0 | 5 | 5 |
| Familia de coordinación | 6 / 2 | 6 (11 puntos emitidos) | 6 (7 puntos emitidos) |
| Indiferencia total | 16 / 4 | **fallo TypeError** | 16 |
| Soporte singular aislado | 2 / 0 | 2 | 2 |

H1 pasa: error sup máximo regular 7.771561172376096e-16, regret interino máximo
3.6245516392174193e-16 (vertex); support 3.398017161766334e-17. Los ocho juegos
adicionales recuperan todos sus vértices aislados con ambos métodos; detalle crudo
en summary.csv/equilibria.csv. Las cuatro tolerancias mantienen 5/5 en el caso regular.
Encontrar todos los vértices no demuestra cobertura de cada punto de familias continuas.

Tests nuevos: **9 pasan**, incluyendo 80 ejemplos Hypothesis deterministas, equivalencia
de payoff agregado, lift/proyección, simetría, round-trip, extremos/NaN, tipo raro y
solver externo. Regresión: 10 polyhedral +12 mixed +12 pure +8 común =42; **51 tests**
en total. `coverage --branch --source=src`: 55 statements y 14 branches, **100%**;
no mide cobertura de benchmarks ni dependencias hermanas. Ruff y mypy pasan.
Se ejecutó además el comando común exacto desde la raíz del repo: ocho tests OK.

Tiempos/memoria quedan en summary.csv y timing.csv. Como orden de magnitud, el lote
regular de cuatro juegos tarda ~0.3s racional frente a ~0.2s vertex bajo tracemalloc,
con picos Python ~110KB frente a ~40KB; usar los CSV para cifras exactas de esta corrida.
Conversión y round-trip forman parte del costo externo. No se declara un speedup
general: métodos entregan objetos distintos fuera del caso aislado y tiempos fluctúan.
Errores externos no se comparan como soluciones rápidas. Memoria excluye asignaciones
nativas de NumPy/SciPy y RSS. Entorno: Linux x86_64, Python3.12.14, AMD EPYC9V74,
9 CPUs virtuales visibles; ejecución secuencial, sin afinidad/threads BLAS controlados.

## 5. Ablations negativas y fallos

1. **Sólo vertex:** indiferencia total genera TypeError ('NoneType' object is not
   subscriptable) en esta combinación de versiones. diagnostics.json conserva mensaje
   y warnings. El juego sí tiene una caja de equilibrios; cero salidas no significa
   cero equilibrios. support recupera sus16 esquinas, pero no representa el continuo.
2. **Sólo regret ex ante:** q=1, c=.5, alpha=0, ambos siempre retiran. Para pi=.01,
   .0001,1e-8, regret ex ante=.005,5e-5,5e-9; regret interino siempre .5. A epsilon=1e-8,
   el último perfil pasa un filtro ex ante pero falla por **50 millones** el umbral
   interino. No hay fallo de equilibrio exacto: para probabilidades positivas exactas,
   cero regret ex ante sí fuerza cero regret de cada tipo. El problema es aproximación.
3. **Sólo listas finitas:** 11 o7 puntos en familia de dimensión2 no son una enumeración
   del continuo. Se mantiene la representación poliédrica, sin seleccionar un equilibrio.

## 6. Prior art: cobertura y límites

Fecha 2026-10-16. Búsqueda web, no revisión sistemática. Consultas registradas aquí:

| Canal / consulta | Evidencia recuperada / limitación |
|---|---|
| Nashpy docs: vertex enumeration, handle degenerate games | Documentación primaria leída; advierte incompletitud de listas en degenerados. |
| Gambit16.4.1: formats.nfgpay, enummixed | Formato primario leído; orden de payoffs y alcance de extremos, no ejecución. |
| SIAM: Enumeration of All Extreme Equilibria of Bimatrix Games | Audet et al.2001, DOI10.1137/S1064827598339086; metadatos y resumen, no réplica del artículo. |
| INFORMS: 10.1287/mnsc.14.3.159 | Harsanyi1967, fundamento de juegos bayesianos. |
| SSRN: Enumeration of Nash Equilibria for Two-Player Games | Avis et al.1365927, ficha recuperada; PDF autor dio error de acceso. No afirmar lectura integral. |
| NBER: Incomplete Information in Macroeconomics 22297 | Angeletos/Lian2016 ficha/resumen; coordinación, no baseline computacional comparable. |
| CEPR: DP3233 | Rochet/Vives2002 ficha recuperada; motivación bancaria, modelo más rico que este juguete. |
| Semantic Scholar: título exacto Avis + Nash enumeration | Sólo coincidencias indirectas en otros artículos; no ficha primaria validada. |
| Papers with Code: Nash equilibrium enumeration | OPGD encontrado pero no comparable; no benchmark equivalente validado. |
| arXiv econ.TH: Nash enumeration | Resultados de matching/redes no comparables, no artículo retenido. |
| arXiv econ.EM/q-fin.EC/math.OC/stat.ME: Bayesian equilibrium enumeration; consultas individuales Nash/coordination | Cobertura pobre: espejos y resultados fuera de alcance, ninguno retenido como evidencia primaria comparable; no inferir inexistencia. |
| Econometrica/JET/GEB: Bayesian normal form equilibrium enumeration | Literatura de equilibrio/aprendizaje y referencias indirectas; no benchmark adicional comparable validado. AER/QJE/JPE/ReStud/JoE no revisados individualmente en este ciclo. |

Harsanyi fundamenta la representación de información; Audet/Avis ya estudian enumeración
extrema; Nashpy implementa un método conocido. Este MVP no reclama novedad de esa
teoría/algoritmo ni revisión exhaustiva. No se equipara la motivación de Rochet/Vives o
Angeletos/Lian a una calibración del presente juego finito.

## 7. Reproducción y límites pendientes

Comando único en README; requirements directos fijados, lock transitorio completo,
configuración y hashes CSV guardados. Notebook ejecutado realmente de arriba abajo
con IPython en proceso y outputs guardados, formato nbformat validado. Figura revisada
visualmente: unidades/leyendas legibles, fallo señalado, escala log explícita; no QA
interactivo/narrow viewport. La habilidad de notebooks guio estructura y captura real;
sus referencias compartidas no estuvieron disponibles, sin impedir este flujo local.

No se ejecutó un solver racional externo, no se verificó un parser Gambit real y no
se mide memoria nativa. Benchmarks pequeños y selectivos, mismos primitives NumPy/SciPy
en parte de los baselines: independencia de implementación no significa independencia
de todos los componentes numéricos. No datos reales, inferencia causal, validación
out-of-sample ni estimación estructural. **Madurez componente S2, programa S2 parcial**.
