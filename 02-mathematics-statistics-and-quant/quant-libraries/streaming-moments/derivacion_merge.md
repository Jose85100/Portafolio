# Fusionar resúmenes en unidades diferentes
## Pregunta, notación y original
Continuamos29Welford/Chan,30escalaexterna,31autoescala. Un resumen de observaciones finitas disjuntas A tiene n_A, exponente e_A, origen a_A, media relativa b_A y suma centrada Q_A, en unidades normalizadas y=x/2^{e_A}. Media μ_A=a_A+b_A. En unidades físicas U, media2^{e_A}μ_A, varianza U², SD U; n y exponentes adimensionales. Asumimos n≪2^53. El contrato no detecta solapamiento: el consumidor garantiza particiones disjuntas.

La expresión original Chan conocida (doi10.1080/00031305.1983.10483115) sobre la misma unidad es
$$\delta=\mu_B-\mu_A,\quad \mu=\mu_A+\delta n_B/(n_A+n_B),$$
$$Q=Q_A+Q_B+\delta^2 n_A n_B/(n_A+n_B).$$
Para derivar, separe Σ_A(y−μ)²=Σ_A[(y−μ_A)+(μ_A−μ)]². El término cruzado es0 porque Σ_A(y−μ_A)=0. Por tanto es Q_A+n_A(μ_A−μ)². Análogo B. Sustituya μ_A−μ=−δn_B/n y μ_B−μ=δn_A/n; suma de cuadrados extra δ²[n_A n_B²+n_B n_A²]/n²=δ²n_A n_B/n. No existe nuevo estimador.

## Brecha y adaptación al estado31
No se pueden fusionar Q_A y Q_B en escalas diferentes directamente. Elegimos E=max(e_A,e_B) entre resúmenes con algún dato no nulo: los ceros no determinan unidad. Si ambos son todo ceros E=0. Sea c_j=2^{e_j−E}. Cada y'_j=c_jy_j, luego a'_j=c_ja_j, b'_j=c_jb_j, Q'_j=c_j²Q_j (derivación31 conservada). Ahora ambas medias están expresadas en la misma unidad y se aplica Chan anterior.
$$a'_j=2^{e_j-E}a_j,\quad b'_j=2^{e_j-E}b_j,\quad Q'_j=2^{2(e_j-E)}Q_j.$$
$$\delta=(a'_B-a'_A)+(b'_B-b'_A),\quad n=n_A+n_B,$$
$$a=a'_A,\ b=b'_A+\delta n_B/n,\ Q=Q'_A+Q'_B+\delta^2 n_A n_B/n.$$
Esto corresponde exactamente al helper rebase y `Moments.merge`. Se calcula SD=2^E sqrt(Q/(n−d)), V=2^{2E}Q/(n−d), d∈{0,1}, n>d. Resumen vacío es identidad; n siempre suma. En aritmética real se conservan media, suma centrada, positividad y asociatividad/commutatividad del resultado estadístico. En máquina NO se conserva igualdad bit a bit por orden de reducción; tampoco se garantiza cota universal de error. Constantes/cero producen SD0. NaN/inf se rechazan al push, d/n inválidos al result.

## Condiciones, negativos y propiedades perdidas
Para resúmenes creados mediante API (no estados construidos arbitrariamente), normalización limita magnitudes. Reescalado puede redondear componentes a0; rounded_to_zero suma diagnósticos anteriores y nuevos, pero no mide toda información perdida ni cota de error. Reutilizar el mismo resumen en ambos lados duplica datos: no independencia ni deduplicación automáticas. La fusión es operación numérica sobre particiones, no inferencia de independencia estadística.

Ejemplo adverso: [1e−300,2e−300] fusionado con [1e300,2e300] descarta cantidades pequeñas al reescalar. SD puede seguir representable, pero sus contribuciones no se recuperan. Entradas redondeadas antes de ingresar siguen irrecuperables. Subnormal [-min,min] produce SD=min; [0,min] posee SD realmin/2 y puede abstenerse std_underflow. Resultado depende del árbol de cómputo; no teorema flotante. Ninguna mejora científica original ni implementación paralela; sólo componente conectable con pruebas.
