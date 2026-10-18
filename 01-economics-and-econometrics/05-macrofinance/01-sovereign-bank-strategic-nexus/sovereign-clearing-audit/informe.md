# Informe — Sovereign Clearing Audit, 2026-10-18

## Revisión actual y decisión de alcance

Base inspeccionada:`e25c2ace7f0085fd20e25d00468535473e80f469`. Se revisaron historial
reciente, estándares S0–S4, README de dominio/macrofinanzas/programa, núcleo común y
los notebooks estructurales de contagio y pagos. No se encontraron AGENTS.md.
Los PR #48/#49/#50 ya profundizaron notebooks y riesgo. **El notebook de contagio
ya implementa Eisenberg–Noe**, no es correcto seguir llamándolo sólo baseline OLS.
El PR #46 ya cerró el contraste racional del juego crediticio. No se modificaron
esos aportes ni se duplicaron sus modelos como supuesta novedad.

El programa Sovereign–Bank Strategic Nexus seguía S1. Se reduce el juego dinámico
propuesto a un **componente estático de balances/pagos** y se monta su primer MVP S2:
exposición soberana exógena, solver modular, contrato de parada, LP/oráculo racional,
controles negativos y conciliación económica. El programa pasa a **S2 parcial**,
no el doom loop dinámico completo. El dominio queda con9 programas S1 y3 con
componentes S2; los35 laboratorios adicionales no se convierten por ello en modelos
estimados o evidencia empírica.

## Pregunta, brecha y falsación

¿Puede un residual de clearing pequeño ocultar errores materiales de pagos, y puede
el impago bruto confundirse con una pérdida externa agregada tras un haircut soberano?
La brecha local es de control numérico y contabilidad, no inexistencia de EN/LP o
de iteraciones monótonas en la literatura. Novedad incremental del repo: integrar
esos controles al programa, preservar la regresión del notebook semanal y producir
contraejemplos reproducibles. No se reclama prioridad científica del método.

H1 ejecutable:30 redes regulares de3 bancos, error L1 iterativo frente a Fraction
≤ancho de cotas+1e-12; error LP–Fraction <1e-7; ancho final≤1e-8; error de reconciliación
de recursos <1e-8 en la malla soberana. La regresión del notebook semanal debe tener
diferencia de impago bruto <1e-8 en sus cinco casos. Ante red casi cerrada, las cotas
deben **rechazar** si no alcanzan precisión en el presupuesto, no afirmar convergencia.
No se exige que el nuevo método sea más rápido ni que todo LP sea preciso.

## Modelo y supuestos económicos

L_ij≥0 indica cuánto debe i a j, diagonal0. l_i≥0 es deuda con acreedores fuera de red,
pbar_i=sum_j L_ij+l_i. Para cada deudor se exige l_i>0, una condición más fuerte que
la regularidad general EN. Bancos sin deuda tienen Pi_i=0. Pi_ij=L_ij/pbar_i.

$$x_i(h)=c_i+(1-h)b_i,\qquad p=F(p)=\min(\bar p,x+\Pi^Tp).$$

E_i=max(x_i+(Pi^Tp)_i-p_i,0). Responsabilidad limitada, prioridad de deuda, recuperación
proporcional y sin costos de quiebra. Cash y soberanos son recursos liquidables al
valor fijo supuesto; no existe decisión de venta, precio endógeno, colateral, garantía,
bailout ni incumplimiento estratégico. Haircut h exógeno, no probabilidad estimada.
Es un mecanismo de clearing estático, **no equilibrio Nash ni modelo macro dinámico**.

No se usan datos observados, TES ni balances de bancos colombianos. No hay estimando
causal, identificación de h, selección de equilibrio ni validación out-of-sample.
Redes, cash y exposiciones son sintéticos y conocidos por construcción. La consolidación
excluye al emisor soberano: no se presenta como contabilidad nacional o bienestar social.

## Control numérico y oráculos

Beta=max_i sum_j Pi_ij<1. En aritmética exacta, min es1-Lipschitz por componente y
||Pi^T||_1=beta, por lo que F es contracción en norma1 y el error está acotado por
||F(p)-p||_1/(1-beta). Es argumento estándar bajo estos supuestos, no teorema nuevo.
Con beta cercano a1 el residual puede ser una mala medida absoluta de error.

Se itera desde0 y pbar; exacto:lo_k≤p*≤hi_k. La anchura L1 acota el error de pagos;
se devuelve el punto medio al cerrar≤1e-8. La implementación usa **flotantes ordinarios**,
no redondeo dirigido: las cotas se contrastan empíricamente, no se venden como un
certificado formal de intervalos. Si no cierran tras10000 pasos, RuntimeError explícito.

LP independiente: maximizar sum(p) sujeto a0≤p≤pbar y(I-Pi^T)p≤x, mediante HiGHS.
Fraction: enumerar conjuntos de default, resolver el sistema lineal de cada conjunto
y comprobar el punto fijo exactamente sobre los **decimales de entrada**. Cap6 bancos
por crecimiento exponencial. Ambos comparten inputs y modelo, no toda su ruta numérica.
Un status de éxito de LP no prueba precisión monetaria en sistemas mal condicionados.

## Diseño, baselines y equidad de comparación

1. Ring3 bancos: cada uno debe.9 a su sucesor y.1 fuera, pbar=1. Cash=(0,.1,.1),
   soberanos=(.1,0,0). Once haircuts de0 a1; config.json guarda inputs.
2. Baseline económico de una pasada:min(pbar,x+Pi^Tpbar). Es un **déficit contractual
   sin cascada**, no otro clearing ni una política factible: puede sobrepagar recursos.
3. Regresión contra la función `experiment` real del notebook semanal ampliado por
   #48; se lee su AST, extrae sólo esa definición y ejecuta cinco shocks. No se editan
   sus celdas ni se reinventa una copia presentada como original.
4.30 redes racionales3x3, l_i=.2, activos y obligaciones en décimas, seed20261018.
5. Anclas.1,.01,.001,1e-9 para diagnóstico de parada, referencia exacta Fraction.
6. Escalabilidad:8/32/128 bancos, ring con ancla.2, recursos.1 por banco, todos en
   default; tres repeticiones de dos cotas, residual sólo, residual ajustado y LP.

Se descartó durante revisión una primera grilla de escalabilidad demasiado fácil,
arrestada por bancos solventes. La grilla final fuerza contracción iterativa. Para
comparación de precisión más justa, residual ajustado usa epsilon*(1-beta)/n como
tolerancia por componente, equivalente a un objetivo L1 epsilon en aritmética exacta.
Residual sin ajustar se conserva como ablation y se marca **no comparable en precisión
global**. No se declara speedup a partir de tolerancias incompatibles.

Entorno:Python3.12.14, Linux x86_64, AMD EPYC9V74,9 CPUs virtuales visibles; ejecución
secuencial, sin afinidad ni control de threads BLAS. Dependencias directas fijadas y
lock de transitivas. Tiempo excluye instalación; memoria tracemalloc excluye native
RSS/HiGHS/BLAS. No comparar esos bytes como memoria total del solver.

## Resultados ejecutados

| Haircut | Pérdida de activo soberano | Déficit bruto una pasada | Impago bruto clearing | Impago acreedores externos |
|---|---:|---:|---:|---:|
|0|0|0|≈0|≈0|
|.5|.05|.05|.5000000031|.0500000003|
|1|.1|.1|1.0000000015|.1000000002|

No interpretar1/.1=10 como multiplicación de pérdida social. Al consolidar, pagos
internos se cancelan:

$$\sum_i x_i=\sum_i(l_i/\bar p_i)p_i+\sum_i E_i.$$

El agregado bruto cuenta repetidamente obligaciones de una misma cadena. En este
ring sin colchones, el acreedor externo absorbe la pérdida directa. Un resultado no
es general a redes con costos de quiebra/precios endógenos. La una-pasada tiene error
de recursos-.09 al haircut total: **no es solución factible**. El clearing tiene error
de identidad~-1.54e-10 y error frente a LP~1.54e-9;186 iteraciones, ancho~9.25e-9.

30 oráculos: máximo error iterativo–Fraction **4.473321268960717e-9**; máximo LP–Fraction
**8.881784197001252e-16**. Cinco regresiones semanales: diferencia máxima **0**.
Los artefactos crudos contienen cada red, vector racional y pagos por banco.

Benchmark final128 bancos, medianas locales de tres repeticiones: dos cotas~.0150s,
residual ajustado~.00771s, LP~.00730s. Picos Python212128/212128/461216 bytes,
respectivamente; ver timing.csv para cada corrida. Residual sin ajustar es más rápido
pero error L1~4.31e-6; ajustado~6.67e-9. Las dos cotas son más conservadoras y lentas,
no una mejora universal de rendimiento. En el ring simétrico el punto medio puede
cancelar errores favorablemente; no extrapolar esa precisión fortuita a cualquier red.

## Ablations negativas y fallos

- Ancla1e-9, recursos5e-10 por banco: verdad racional p_i=1/2. Residual sólo acepta en
  **una iteración**, residual L1~1.5e-9 y error L1~1.5. Las dos cotas rechazan tras10000
  pasos, ancho~2.99997. El MVP **no resuelve eficientemente** ese extremo.
- En el mismo caso, LP reporta éxito pero error L1=1.5: su tolerancia de factibilidad
  permite violaciones pequeñas frente a un sistema muy sensible. No es prueba de un
  bug general de HiGHS ni se oculta como oráculo correcto en todos los regímenes.
- Ancla.001 también puede agotar presupuesto según criterio; todos los estados,
  aceptados y rechazados, quedan en near_closed.csv. No se descartan casos desfavorables.
- Redes cerradas o cuya ancla se pierde al redondear se rechazan; no se escoge
  arbitrariamente entre múltiples clearings de un sistema no regular.
- Ruff detectó nombres ambiguos de variables durante desarrollo; se corrigieron.
  Una ejecución del comando común desde carpeta equivocada falló; se reejecutó desde
  raíz y pasó. Los logs finales corresponden a ejecuciones completas satisfactorias.

## Tests, cobertura y revisión

**10 unit tests nuevos +8 comunes pasan**, con60 ejemplos Hypothesis deterministas
de oráculos/monotonicidad, zero-debt, NaN/negativos, anclas inválidas, presupuestos,
fallo de LP y cap racional. Ruff y mypy de src pasan. Coverage:121/122 statements,
42 branches con una ruta parcial, **99% combinado**. No se ejercitó el guard final
de ausencia de candidato racional; no se mide cobertura de scripts o dependencias.
Se ejecutó el comando común exacto desde raíz:
`python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v`.

Revisión técnica local: se inspeccionaron orientación de L/Pi, identidad consolidada,
oráculos, presupuestos y comparabilidad de tolerancias. No equivale a aprobación
humana independiente. Checklist completo y hashes CSV verificados antes de publicar.
Las guías de notebooks y visualización orientaron ecuaciones, controles y figura;
referencias compartidas de esas guías no estaban disponibles. Notebook con código de
clearing realmente ejecutado, outputs guardados y nbformat validado; figura inspeccionada
visualmente. No se afirma QA de viewport estrecho ni revisión científica externa.

## Prior art y cobertura real (2026-10-18)

Revisión parcial, no sistemática. Se consultaron fuentes primarias y metadatos/resúmenes;
no se afirma lectura integral o reproducción de todos los artículos.

| Canal / búsqueda | Resultado y límites |
|---|---|
| INFORMS EN2001 | Página primaria y resumen sobre clearing/regularidad; método ya conocido y ya presente en notebook del repo. |
| AER Brunnermeier et al.2016 | Ficha primaria DOI10.1257/aer.p20161107 y autores; motivación de nexus/ESBies, **no** modelo replicado aquí. |
| NBER21993/21843 | Citas por buscador; apertura directa403. Se registra bloqueo, no se afirma lectura completa. |
| CEPR DP11317 | Ficha/resumen accesibles; versión de autores distinta en ficha CEPR, BibTeX del artículo sigue lista AER verificada. |
| SSRN EN173249/993629 | Fichas recuperadas por búsqueda; apertura173249 devolvió403. |
| arXiv math.OC | Calafiore et al.2201.12898v4, resumen primario: clearing dinámico/LP. Alcance diferente, aquí sólo estático. |
| arXiv q-fin.MF/RM | Feinstein et al.1708.01561v4, sensibilidad a obligaciones; no se reproduce su experimento empírico. |
| arXiv econ.EM/econ.TH/q-fin.EC/stat.ME | Consultas específicas soberano/redes/clearing: resultados indirectos de reconstrucción de redes y deuda, sin benchmark directamente comparable validado en estas categorías. No inferir inexistencia. |
| Semantic Scholar EN/Systemic Risk | No ficha directa validada recuperada; cobertura insuficiente. Una consulta combinada dio resultados irrelevantes y se reformuló. |
| Papers with Code | Perfil de autor Feinstein con modelos dinámicos, sin benchmark estático equivalente validado. |
| Código de autores NEVA | README primario leído; EN como caso especial, no se instaló/ejecutó NEVA ni se reclama superioridad. |
| GEB Strategic default in financial networks | Ficha por buscador/repositorios universitarios; publisher403 al abrir. Juego estratégico más amplio que este clearing. |
| JoE/JET y otras revistas solicitadas | Consultas acotadas sin nuevo baseline equivalente validado. QJE/JPE/ReStud no revisadas individualmente en este ciclo; revisión exhaustiva pendiente. |

Seis entradas reales en referencias.bib. La formalización de balance/parada y los
contraejemplos son aporte de integración verificable, no prioridad del modelo o algoritmo.

## Madurez y riesgos pendientes

**Componente estático S1→S2; programa S2 parcial**. El juego dinámico fiscal-bancario,
garantías, precios y evidencia empírica siguen S1. Datos sintéticos y una familia de
redes no validan el mecanismo en Colombia. No equivaler equilibrio numérico a teorema,
gross unpaid a bienestar, correlación a causalidad ni esta corrida a estrés regulatorio.
Fuera de alcance: colateral, fire sales, seniority múltiple, multi-moneda, recuperación
con costos, bancos estratégicos, rescates endógenos y calibración de activos soberanos.
