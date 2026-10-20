# Informe crítico — Coupled Clearing Audit

Fecha: 2026-10-20. Evidencia: implementación y escenarios sintéticos, no
observaciones bancarias. Componente S2; programa Sovereign–Bank Strategic Nexus
S2 parcial, sin promoción a S3 o S4.

## 1. Inspección previa, arquitectura y brecha

Base revisada: `dd5dc42984ca98ecf3ccda47a21dfd4008afe0bb`. Se inspeccionaron
commits recientes, README del dominio/programa, RESEARCH_STANDARDS.md,
THEORY_COMPARISON_PROTOCOL.md, núcleo común, solvers EN/precio y las nuevas
herramientas de revisión de #55/#56. No se encontraron AGENTS.md en el árbol
clonado. No se reutilizó el inventario inicial de12 S1: actualmente el README
declara9 S1 y3 programas con componentes S2. Los nuevos laboratorios de
refutación y el auditor determinista no se confunden con revisión humana.

La revisión fue dirigida al mecanismo elegido; no se afirma haber reejecutado
todos los notebooks. El auditor estático sí inspeccionó47 proyectos:75 avisos
medios,2 bajos,ninguno alto. Son heurísticas textuales, no pruebas semánticas.
El reporte crudo se conserva y el pipeline lo reproduce sin modificar proyectos.

El componente de #52 resuelve EN a precios dados; #58 enumera precios de un
activo sin enlaces. Su acoplamiento simultáneo permanecía S1. Este ciclo lo
lleva a un prototipo S2 para1–4 bancos, preservando los componentes anteriores.

## 2. Pregunta, hipótesis y fuentes

Pregunta: ¿los incumplimientos interbancarios alteran los precios de liquidación
y el shortfall frente a suponer cobros nominales completos?

- H1: recuperar tres precios analíticos del fixture asimétrico con error≤1e-10
  y residual conjunto de pagos/precio≤1e-9.
- H2: congelar cobros nominales subestima en al menos.05 el impago externo
  de la rama baja y produce un vector no factible para el sistema conjunto.

Es falsación de una inferencia computacional simplificada, no refutación de
una escuela económica o de un teorema cuyas hipótesis se rompen.

Eisenberg–Noe(2001) fundamenta el clearing. Cifuentes–Ferrucci–Shin(2005)
estudia precios, ventas y solvencia. Feinstein(arXiv1506.00937v2) define
liquidación mínima con pagos recibidos y múltiples activos; su Assumption3.1
es el antecedente directo. La enumeración de esta reducción es una integración
incremental del repo, no prioridad científica ni el algoritmo completo del paper.
Bichuch–Feinstein incorpora préstamos/colateral, fuera de este MVP. Brunnermeier
et al.(2016) es referente del vínculo soberano-bancario, no un modelo replicado
aquí. Shleifer–Vishny(2011) ofrece la interpretación económica de fire sales.

Seis entradas reales en referencias.bib. Cobertura y bloqueos en
results/search_log.md: SSRN/NBER403; HTMLarXiv deshabilitado pero PDF primario
accesible; fichas SemanticScholar/PWC no validadas; cobertura parcial de
categorías y revistas. No se afirma revisión exhaustiva ni ausencia de prior art.

## 3. Modelo y vertientes comparables

L_ij es deuda del banco i al banco j; o_i deuda externa. Definimos deuda total
pbar_i=sum_j L_ij+o_i,Pi_ij=L_ij/pbar_i, caja c_i, stock s_i y precio q.
Para deudores con saldo0 se usa una filaPi nula. Los pagos son pro-rata.

\[
p_i=\min(\bar p_i,c_i+qs_i+(\Pi^Tp)_i),\quad
\gamma_i=\min(s_i,[\bar p_i-c_i-(\Pi^Tp)_i]^+/q),
\quad q=\max(q_{min},q_0-a\sum_i\gamma_i).
\]

Venta uniforme al precio final, no VWAP ni ejecución secuencial. Los bancos
siguen una regla mínima, no maximizan estratégicamente precios. No hay crédito,
ventas cortas, colateral, impuestos, quiebra costosa, garantías o política fiscal.
El activo común podría interpretarse como una cartera homogénea, pero no se
ha calibrado a TES ni modelado default soberano. El piso es demanda externa
elástica supuesta; su costo no está presupuestado ni se recomienda como política.

Vertientes: EN condicionado a precio es un baseline correcto para su pregunta;
la ablación de cobros nominales asume solvencia de todas las contrapartes y
puede fallar al aparecer defaults; el sistema conjunto permite que éstos
alteren ventas y precio. La rama alta coincide cuando todos pagan nominal:
un control positivo, no una victoria universal del modelo más complejo.

## 4. Existencia, unicidad condicionada y enumeración

Para q fijo, el ancla externa hace contractivo el mapa EN en norma1, por lo
que su vector de pagos es único. Esto no implica unicidad al endogeneizar q.
El mapa conjunto es continuo sobre [0,pbar]×[piso,q0] y se aplica en esa caja;
Brouwer asegura existencia en este modelo. Son argumentos estándar bajo los
supuestos declarados, no un nuevo teorema de investigación.

Cada banco puede ser D(default),V(solvente que vende),Z(solvente sin ventas).
Para un conjunto D dado:

\[
p_D=(I-\Pi_{DD}^T)^{-1}(c_D+\Pi_{SD}^T\bar p_S+q s_D)=u_D+v_Dq.
\]

Los cobros son afines. La solvencia y el signo del gap producen desigualdades
lineales en q. Se intersectan con [piso,q0] usando Fraction. En cada régimen
la venta agregada es A+B/q; los precios interiores satisfacen
q²−(q0−aA)q+aB=0. Se evalúan ambas raíces, el piso y la pertenencia al intervalo.
En aritmética exacta, todo equilibrio tiene uno de estos regímenes; los bancos
indiferentes en una frontera pueden generar duplicados.

El código usa Decimal80 para raíces y convierte a float. Detecta raíces
cuadráticas demasiado próximas, audita residual y elimina duplicados numéricos.
**No es una certificación de intervalos con redondeo dirigido**, ni una prueba
formal de completitud numérica para raíces casi indistinguibles entre regímenes.
Contrato:1–4 bancos, ancla externa≥1%,inputs≤100,piso≥1e-6. El costo es
exponencial3^n; se rechaza n>4. Las redes casi cerradas quedan fuera, no resueltas.

## 5. Diseño, datos y comparaciones justas

Datos sintéticos, seed20261020. Fixture:L12=L21=.1;o=(.1,.1);c=(0,.02);
s=(1,.2);a=.8;q0=1;piso=.05. ConfigJSON y SHA256 guardados.
Tres referencias complementarias:

1. Soluciones analíticas derivadas a mano para los regímenes del fixture.
2. Pagos del `rational_clear` anterior al precio candidato y reducción sin
   enlaces al `equilibria` anterior; ambos módulos reales se importan y ejecutan.
3. Baseline numérico independiente: EN de dos cotas del repo dentro de una
   malla501 y SciPyBrent sobre la ecuación de precio reducida. No se presenta
   como censo exhaustivo cerca de tangencias.

Doce mercados aleatorios de2 bancos guardan parámetros y discrepancias.
Sensibilidad:21 niveles de caja del banco1 de0 a.10; cada raíz se guarda por
separado. Tolerancias internas1e-6/1e-9/1e-12 se contrastan a los precios del
censo. n2/3/4 con3 repeticiones y agregados externos/stock constantes evitan
confundir cambiar tamaño con aumentar el shock. Se mide tiempo de pared con
tracemalloc y pico de asignaciones Python; no RSS ni memoria nativa completa.

## 6. Resultados ejecutados

| Precio | Pagos de bancos | Defaults | Impago externo | Impago bruto |
|---:|---|---:|---:|---:|
|.05|(.086666666667,.073333333333)|2|.12|.24|
|.144405323239|(.2,.148881064648)|1|.025559467676|.051118935352|
|.825576411922|(.2,.2)|0|0|0|

Las referencias analíticas son .05,(.92−sqrt(.3984))/2 y(1+sqrt(.424))/2.
En la rama baja los pagos son13/150 y11/150. Residual conjunto máximo del
fixture1.67e-16. Las regresiones ejecutadas contra los dos módulos anteriores
tienen discrepancia máxima0 en estas entradas; no implica exactitud formal
flotante general. Los12 contrastes numéricos recuperan todos los precios de
esos casos, con diferencia máxima2.2426505097428162e-13.

Cobros congelados dan precios.05,.109516506075,.825576411922. En la rama baja,
impago externo.06, equity mínimo−.035 y residual.035. Por tanto **no es otro
equilibrio conjunto**. En la rama interior, su residual es.0595165 y el precio
difiere en.0348888. El baseline EN a q=1 tiene pagos solventes correctos para
ese precio, pero residual de mercado.144. La iteración superior encuentra
solo la rama alta; un punto convergente no acredita unicidad.

La identidad sum(c+qs)=pago_externo+sum(E) se cumple también con E negativo;
no basta para afirmar factibilidad. En las soluciones conjuntas se verifica
equity no negativo salvo redondeo y residual pequeño. Impago bruto, impago
externo y pérdida marcada no se equiparan ni se suman como pérdida social.

En la rama baja, al reducir la tolerancia EN de1e-6 a1e-12, el error L1 de
pagos baja de7.63e-8 a7.28e-14; el precio inducido queda en el piso. Es
estabilidad numérica de este control, no estabilidad macroeconómica.
Costos:27 registros crudos en results/costs.csv. La enumeración puede ser
más rápida que malla anidada para estos tamaños, pero no se extrapola ni se
compara una sola raíz de Picard con tres raíces como tareas equivalentes.

## 7. Controles negativos, fallos y cobertura

Sin impacto o con caja suficiente queda q=1. Sin enlaces se reproduce el MVP
de precios previo. El fixture simétrico conserva.05,.2,.8. En el caso sin
enlaces con raíz tangente.5, la malla101 solo encuentra el piso: contraejemplo
a detectar todas las raíces por cambios de signo, no refutación de la literatura.

Tests:8 métodos propios y70 ejemplos Hypothesis (oráculo de pagos,monotonicidad
de la mayor raíz,regresión sin enlaces),permutación,matriz singular artificial,
casos nulos,NaN/Inf/negativos,ancla insuficiente y rechazo del tamaño5.
Más8 comunes+10 EN+9 mercado anterior=35 tests financieros. Cuatro tests del
auditor estático elevan a39 los métodos del comando completo.
Ruff(src/tests/benchmarks) y mypy estricto(src) pasan.
Cobertura propia combinada96%:144/148 statements,64 ramas,5 parciales.
No se ejecutaron cuatro guardas numéricas finales de residual/duplicados/
separación/no-raíz ni todas las transiciones de clasificación; no se declara100%.

Comando común solicitado también ejecutado literalmente desde la raíz:

```bash
python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v
```

Fallos de desarrollo corregidos:imports locales provocaron E402 antes de añadir
excepciones justificadas por carpetas históricas sin paquete; una ruta inicial
al nuevo auditor fue incorrecta. Los logs finales son de ejecuciones completas
exitosas; esos intentos no se contabilizan como validación. El notebook tiene
16 celdas,6 de código,ejecutadas realmente con IPython y figura PNG visible.
No se ha reejecutado todo el repositorio; tampoco hubo revisión humana independiente.

## 8. Limitaciones, identificación y riesgos económicos

La complejidad limita el prototipo a redes pequeñas y un activo. No identifica
impacto,liquidez ni selección de equilibrio con datos. Un factor común puede
producir pérdidas conjuntas sin contagio causal. Para distinguirlo harían falta
balances granulares,exposición predeterminada,shock exógeno de liquidez y controles
contra endogeneidad; ese diseño no se presenta como experimento ejecutado.

Sin bienestar de compradores,preferencias y costo fiscal no se pueden ordenar
equilibrios por bienestar ni recomendar subsidios de precio. La iteración
computacional no es una trayectoria económica observada. Ni multiplicidad ni
precios altos demuestran colusión. El piso no es un seguro de liquidez gratuito.
El modelo completo de Feinstein tiene condiciones suficientes de unicidad que
no se satisfacen aquí; la multiplicidad no las refuta.

Hardware,Python,CPU y número de CPUs lógicas expuestas figuran en metadataJSON;
no se controló carga/afinidad ni se usó GPU. Python3.12/Linux y dependencias
fijadas; Docker,Windows,otros intérpretes y redes>4 no fueron validados.

## 9. Cierre de madurez

Se amplía S2 con el acoplamiento antes pendiente. El programa sigue S2 parcial;
colateral,préstamos,múltiples activos,juego fiscal e identificación siguen S1.
La tabla MVP.md declara el alcance y el checklist. Publicación por rama/PR,
CI y respeto a cambios concurrentes; cualquier autorrevisión automatizada se
identifica como tal, no como aprobación independiente.

Siguiente iteración recomendada: mejorar la precisión y la interpretación antes
de ampliar el modelo fiscal: computational-economics para certificación de
raíces;05-macrofinance para colateral presupuestado;03-game-theory para decisiones
de garantías sin confundir clearing mecánico y comportamiento estratégico.
