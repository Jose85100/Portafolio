# Informe crítico — Fire-Sale Price Audit, 2026-10-19

## 1. Resultado y pregunta

MVP ejecutado: censo de puntos fijos de un mercado de liquidación mínima,
frente a precio fijo, Picard desde extremos y malla+Brent. La pregunta no es
si existen fire sales —mecanismo conocido— sino qué conclusiones de selección
puede ocultar el baseline a precio exógeno del repo.

Hipótesis H1: fixture de dos bancos con caja0,deuda.1,stock1 cada uno,
impacto.8,precio fundamental1,piso.05 debe producir precios {.05,.2,.8}
con error≤1e-10 y un inicio superior solo recupera uno. H2: al subir la deuda
a .15625 por banco, la raíz doble .5 debe aparecer en el censo. Los tests
verifican ambos. Son resultados de simulación/algebra del modelo, no evidencia
de crisis bancarias ni una nueva proposición de teoría económica.

## 2. Inspección previa y no duplicación

Base verificada: f1658d32226a517f2e7e88652120001eeea6f47d. Se inspeccionaron
commits recientes, RESEARCH_STANDARDS.md, README general/programa, núcleo
econlab.py, inventario de carpetas y los componentes de macrofinanzas pertinentes.
No se encontraron AGENTS.md en el árbol clonado. Los avances #52,#53,#54
están presentes: no se reutilizó el estado histórico12 S1. El inventario
declarado actual es9 programas S1 y3 S2 parciales. La nueva guía OLS/IV de #54
no estima precios de liquidación. El notebook semanal de liquidez ya resuelve
EN, y declara que no tiene fire sales. No se reetiqueta como baseline OLS.
El clearing de #52 fija x=c+(1-h)s y tampoco resuelve precios.

La revisión fue dirigida al componente elegido; no se afirma haber reejecutado
todos los notebooks o auditado íntegramente los12 programas y35 laboratorios.
Se mantienen intactos los archivos anteriores, salvo enlaces en dos README.

## 3. Estado del arte y brecha defendible

Eisenberg–Noe(2001) proporciona clearing de pagos para obligaciones dadas.
Cifuentes–Ferrucci–Shin(2005) estudia ventas, precios y restricciones de solvencia.
Feinstein(arXiv1506.00937,v2) trata múltiples activos y estrategias de liquidación,
incluida la necesidad mínima de efectivo; sus hipótesis de unicidad son
condicionales. El MVP restringe a un activo sin enlaces y no satisface por
construcción todas las condiciones que garantizarían unicidad en modelos amplios.
No es una refutación de esos teoremas.

Shleifer–Vishny(2011) ofrece interpretación y revisión de fire sales;
Diamond–Rajan(2011) añade incentivos a retener activos/contraer crédito, ausentes
aquí. Bichuch–Feinstein(2018) modela préstamos y colateral, también ausentes.
Brunnermeier etal(2016) es el referente del vínculo soberano-bancario, que este
componente no reproduce. Vuillemey(CEPR17933) analiza apoyo de precios en una
CCP histórica; no justifica atribuir bienestar o gratuidad al piso de este MVP.

Brecha **del repo**: censo reproducible de precios con regímenes y tangencias,
no una nueva teoría de fire sales. Ver referencias.bib(8 entradas reales) y
results/search_log.md. SSRN/NBER403, fichas SemanticScholar/PWC no validadas,
cobertura parcial de categorías arXiv y revistas: no revisión exhaustiva.

## 4. Modelo, supuestos y existencia

Banco i: caja c_i≥0,deuda externa D_i≥0,unidades s_i≥0. Una fecha, un numerario,
activo homogéneo, liquidación uniforme al precio final q. Sin deuda interbancaria,
compras bancarias, ventas cortas, crédito, impuestos ni costos de liquidación.
Se vende solo para cubrir d_i=(D_i-c_i)^+, hasta agotar s_i:

\[
\gamma_i(q)=\min(s_i,d_i/q),\quad F(q)=\max(q_{min},q_0-a\sum_i\gamma_i(q)).
\]

q_min>0,a≥0,q0≥q_min son parámetros, no estimaciones. F es continua y no
decreciente en el intervalo. F(q_min)-q_min≥0 y F(q0)-q0≤0; el teorema del
valor intermedio asegura al menos un punto fijo de esta formulación. No asegura
unicidad, atractivo dinámico ni implementación de un equilibrio estratégico.
La clasificación local de Picard usa pendientes laterales, no estabilidad
financiera ni probabilidades de selección.

Los quiebres d_i/s_i dividen los regímenes. Con stock saturado A y necesidad
no saturada B, cada raíz interior resuelve q²-(q0-aA)q+aB=0. Se verifican
los intervalos cerrados y se añade el piso solo cuando corresponde. Esto
enumera las soluciones de la ecuación escalar en aritmética exacta. El código
usa coeficientes/discriminantes Fraction de strings decimales, Decimal64 para
sqrt y float para resultados. **No es una certificación formal flotante.**
Inputs limitados a [0,1e6],piso≥1e-8; se rechazan residual>1e-10 y raíces
distintas separadas<1e-10. No se promete cubrir arbitrarias escalas/precisiones.

El piso implica demanda externa elástica a ese precio. Puede interpretarse
como valoración residual postulada; si se interpreta como respaldo público,
faltan presupuesto, elegibilidad e incentivos. No lo llamamos rescate óptimo.

## 5. Diseño y comparaciones justas

Seed20261019, configJSON y SHA256 guardados. Escenarios deterministas:101
niveles equiespaciados de deuda0:.002:.2 por banco, más .15625. Cada rama se
guarda por separado, sin convertir escenarios en intervalos de confianza.
Controles:impacto0,caja suficiente,piso.3,pliegue y deuda .15624999.
40 mercados de4 bancos se contrastan con malla4001+scipy.optimize.brentq.
Este contraste no es un oráculo exhaustivo cerca de tangencias; los fixtures
analíticos cubren precisamente ese punto ciego.

Escala:n=8,32,128,3 repeticiones. Stock agregado2; financiación agregada cercana
a .12 con heterogeneidad periódica explícita en el script. Misma entrada para
todos los métodos a cada n. Se registra tiempo de pared con tracemalloc activo,
máximo de asignaciones Python y residual. No RSS ni memoria nativa completa.
No se compara velocidad de un censo de3 raíces con una raíz como si fueran
problemas equivalentes. No se ejecuta el solver multiactivo íntegro de Feinstein.
La iteración y malla son baselines locales identificados, no fallos atribuidos
a una implementación de la literatura que no se ha probado.

Regresión ejecutada contra `sovereign-clearing-audit`:misma deuda externa,
matriz de enlaces cero,a4 precios. Diferencia de pagos máxima8.33e-17.
Esta es una reducción real y deliberadamente estrecha, **no acoplamiento EN/precio**.
OLS,bootstrap y ECL del núcleo no resuelven el problema de raíces: la suite
común sí se ejecuta, pero no se fabrican RMSE/causalidad no pertinentes.

## 6. Resultados numéricos ejecutados

| q | Ventas | Pago externo | Impago | Equity marcado | Pérdida marcada |
|---:|---:|---:|---:|---:|---:|
| .05 |2|.1|.1|0|1.9|
| .2 |1|.2|0|.2|1.6|
| .8 |.25|.2|0|1.4|.4|

Residual máximo del fixture5.55e-17; error de identidad de balance0.
Precio fijo1:ventas.2,impago0,residual.16. Una actualización da .84, aún
no equilibrio. Picard superior converge .8, inferior queda .05; la raíz .2
es inestable para esa iteración. No se elige arbitrariamente una como pronóstico.

Malla101 y1001 recuperan3/3 raíces en el fixture principal:resultado favorable
al baseline. En el pliegue recuperan1/2 (omiten.5); cerca del pliegue1/3
(omiten.4998735088935933 y .5001264911064067). La enumeración recupera ambas.
Impacto0 o caja suficiente:única raíz1. Piso.3:única raíz.8, no tres.
La multiplicidad es condicional y no un resultado universal de ventas forzadas.

40/40 contrastes no degenerados coinciden en número de raíces,error máximo
de precio4.569344902449757e-12. No extrapolar esto a todos los parámetros.
La figura `results/comparison.png` muestra curvas,piso y pliegue; se inspeccionó
visualmente y se separaron los símbolos estables/inestables, sin inventar bandas.

Costos:ver las27 observaciones crudas en results/costs.csv. Las medianas
dependen del host; el notebook imprime las mediciones sin fijar promesas de
tiempo. La enumeración es O(n²) y puede ser más lenta que malla y Picard en
estos tamaños. El aporte es cobertura de raíces críticas, no aceleración.

## 7. Tests, cobertura y entorno

9 métodos propios pasan,120 ejemplos Hypothesis deterministas:permutaciones,
identidad de balance, monotonicidad del mayor precio frente a caja, cambio de
unidades, división de bancos idénticos. Casos dirigidos:nulos,NaN/Inf,longitudes,
presupuesto,quiebres,fold,ambos lados del fold. Más8 tests comunes y10 del
clearing previo(60 ejemplos generados anteriores):27 métodos totales.
Comando común solicitado, también ejecutado literalmente desde la raíz:

```bash
python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v
```

Cobertura propia:96% combinada,111/114 statements y46 ramas,4 parciales.
No se cubrieron tres guardas de error numérico(separación,residual,no-raíz)
ni todas las transiciones de una condición del piso; no se anuncia100%.
Ruff(src/tests/benchmarks) y mypy estricto(src) pasan.

Python3.12.14,Linux x86_64,AMD EPYC9V74,9CPU lógicas expuestas por el entorno;
no se controló afinidad/carga del host. El modelo del CPU,versiones y lock
transitivo quedan registrados. El MVP no necesita GPU ni fuentes privadas.
Notebook15 celdas,6 de código realmente ejecutadas con IPython,7 outputs
incluyendo la imagen. La ejecución automática de CI proporciona una segunda
ruta de ejecución del notebook cuando está verde; no se afirma antes de verlo.

## 8. Fallos, ablations negativas y riesgos

Fallos de desarrollo corregidos:primer pipeline antes de crear benchmarks;
primer benchmark duplicó clave price al construir dict. No se presentan como
validaciones exitosas. Tras corregir, se ejecutó el comando completo.

Fallos intencionales revelados:convergencia superior no prueba unicidad,
una pasada no satisface el punto fijo,malla finita pierde raíces dobles y
pares cercanos. El método propuesto tampoco vence siempre:es más costoso,
restringido a un activo y requiere un piso positivo. No hubo benchmark n>128,
ejecución Windows, prueba de precisión arbitraria ni revisión humana independiente.

Supuestos económicos fuertes:precio único de ejecución;carteras homogéneas;
demanda exógena con piso;ventas sin respuesta estratégica de compradores;
obligaciones externas exógenas;ausencia de préstamos,garantías y red de pagos.
No hay identificación de impacto ni descomposición de riesgo fiscal frente
a liquidez. El activo no es deuda soberana real por etiquetarlo así.

La identidad sum(c+qs)=sum(p+E) es contable dentro del sector. La pérdida
marcada puede ser transferencia/reevaluación y no mide bienestar. Ni precios
múltiples ni precios altos demuestran colusión. Ningún resultado se interpreta
como recomendación de inversión,capital regulatorio o política óptima.

## 9. Madurez y cierre

Nuevo componente S2,programa S2 parcial. Acoplamiento EN/precios,múltiples
activos,optimización,juego fiscal e identificación siguen S1. Los archivos
obligatorios y outputs están presentes; checklist en MVP.md. Integración mediante
rama/PR con CI, sin modificar cambios concurrentes ni afirmar revisión independiente.

Siguiente iteración recomendada: acoplar la liquidación al cobro interbancario
en05-macrofinance; optimizar y certificar el censo en computational-economics;
formular garantías con presupuesto explícito en03-game-theory.
