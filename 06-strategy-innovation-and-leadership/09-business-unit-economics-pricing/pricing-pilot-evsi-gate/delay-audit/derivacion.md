# Derivación y regla de decisión

En cada precio `j∈{A,B}`, la conversión latente es `p_j ~ Beta(α_j,β_j)`, y el margen unitario por conversión es `m_j≥0`. Un piloto asigna `n` oportunidades independientes a cada brazo. El conteo es beta-binomial:

`P(K_j=k) = C(n,k) B(α_j+k, β_j+n-k) / B(α_j,β_j)`.

Tras observar `k`, la media posterior de conversión es `(α_j+k)/(α_j+β_j+n)`, por lo que el valor marginal por periodo es `v_j(k)=m_j(α_j+k)/(α_j+β_j+n)`. La enumeración de ambos conteos produce `q = Σ_k Σ_l P(K_A=k)P(K_B=l) max(v_A(k),v_B(l))`. Por independencia de brazos, la probabilidad conjunta es el producto. Su masa debe ser uno salvo error numérico.

Sin piloto, el mejor margen esperado por periodo es `m0=max(m_A α_A/(α_A+β_A), m_B α_B/(α_B+β_B))`. Durante horizonte `H`, lanzar ahora vale `V_now=H*m0`. Si el estudio tarda `d` periodos y produce decisión al final, quedan `H-d` periodos para capturar contribución; con costo de estudio `c`, `V_pilot=(H-d)*q-c`. La ganancia comparativa correcta es `Δ=V_pilot−V_now`. El gate es **seguir con piloto si Δ>0; ajustar el diseño si hay información potencial pero Δ≤0 por costo/demora; cerrar el piloto si la opción inmediata domina y no hay flexibilidad material adicional**. El modelo no decide si lanzar, ajustar o cerrar después del piloto con pérdidas/costos; representa sólo elegir entre el piloto y la mejor acción inmediata.

Despejando `Δ=0`, el umbral de demora que hace indiferente el piloto es `d*=H−(H*m0+c)/q`, cuando `q>0`. Para `d<d*`, piloto supera a acción inmediata; para `d>d*`, acción inmediata supera; limitar `d*` al rango `[0,H]` es apropiado al reportar una demora operable. Este umbral no es el punto donde el valor absoluto del piloto cae a cero, que sería `(H-d)q-c=0` y respondería otra pregunta.

EVSI clásico sin demora es `H*q−H*m0≥0`, pues el decisor puede ignorar la señal. Esta extensión puede producir `Δ<0` por costo `c` o pérdida de horizonte `d*q`, y ya no está protegida por la no negatividad de EVSI. El costo de demora frente al mismo estudio sin demora es exactamente `d*q` en este modelo. La unidad de `m_j` es contribución abstracta por oportunidad y periodo; al multiplicar por periodos resulta valor agregado en las mismas unidades abstractas que `c`. No se interpreta como moneda.

**Sensibilidad y numerics.** Se mantiene la media Beta al escalar concentración conjunta por `κ>0`: `(α,β)→(κα,κβ)`. La media inicial no cambia, pero sí la predictiva del piloto. Se usa `fsum` en las sumas de utilidades y masa. `lgamma` calcula coeficientes beta-binomial en log-escala. Se registra desviación de masa y se prueba tolerancia. No se trunca una EVSI negativa diminuta sin conservar el residual: `evsi_negative_roundoff` sólo marca un residual menor que `1e-10*max(1,|V_now|)`.

**Supuestos identificadores:** tasas y márgenes estables durante H, brazos independientes e intercambio aleatorio, misma población elegible, muestra completa, aprendizaje sólo al final, ningún ingreso durante estudio, horizonte conocido, riesgo neutral, sin descuento. Violaciones pueden cambiar q, costo de demora y decisión.
