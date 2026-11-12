# Ciclo2nov: ¿reparar la cobertura bajo colas vale su coste?

## Candidatas y alcance
Intervalo bootstrap: flexible, pero cobertura finita no acreditada con colas. Detector de ruptura: relevante, necesita protocolo temporal y no resuelve colas estacionarias. Cota con cuarto momento acotado: seleccionada, deriva una garantía transparente para t5 y permite medir su precio. Clasificación: adaptación de ingeniería y auditoría, no contribución estadística original. Reutilizamos exactamente los 3.240 casos de prueba del 1 de noviembre, dentro del mismo proyecto y con insumos simulados.

## Fórmula original y limitación
El pivote $\chi^2$ del1nov requiere normalidad IID. La t5 tiene varianza finita y kurtosis de Pearson9 (NIST), de modo que falla esa ley pivotal aunque el objetivo monetario siga dependiendo de v. Propuesta: estimador por diferencias de pares disjuntos, no una kurtosis ajustada sobre la misma muestra.

## Derivación paso a paso
Sean $X_i\overset{iid}{\sim}(\mu,v)$, $v>0$, cuarto momento central $\mu_4\le Kv^2$, K≥1 conocido externamente. Para m=⌊n/2⌋, $W_j=(X_{2j}-X_{2j-1})^2/2$ y $\hat v_P=m^{-1}\sum_jW_j$. La resta elimina μ. Si U=X−μ y V=X'−μ, independientes y centrados,
$E(U-V)^2=2v$,
$E(U-V)^4=EU^4+EV^4+6EU^2EV^2=2\mu_4+6v^2$,
pues los términos cúbicos cruzados contienen EU o EV=0.
Por tanto $EW=v$, $EW^2=(\mu_4+3v^2)/2$ y $\operatorname{Var}(W)=(\mu_4+v^2)/2\le(K+1)v^2/2$. La independencia entre pares da $\operatorname{Var}(\hat v_P)\le(K+1)v^2/(2m)$.
Aplicando Chebyshev: $P(|\hat v_P-v|\ge av)\le(K+1)/(2ma^2)$. Para δ=1−confianza, elegimos $a=\sqrt{(K+1)/(2m\delta)}$.
Al invertir $|\hat v_P-v|\le av$, obtenemos $\ell=\hat v_P/(1+a)$ y $u=\hat v_P/(1-a)$ si a<1. Si a≥1, no hay cota superior finita: usamos +∞ antes de intersectar el dominio externo[0,16]. No sustituimos a por un valor conveniente para estrechar el intervalo.

## Propiedades conservadas y perdidas
Intervalo tiene cobertura ≥1−δ bajo IID/cuarto momento acotado; se conecta al mismo solver minimax sin cambiar J ni RE. No es un intervalo normal exacto ni el más estrecho. K es Pearson (normal3,t5=9), no exceso. v,ℓ,u yW tienen unidades de shock²; a,K,m,δ son adimensionales. Antes del clipping conserva traslación, escala cuadrática e intercambio dentro de cada par. No es invariante a permutación arbitraria: el emparejamiento temporal fijado es parte del contrato. Si n impar se descarta la última observación. Pares correlacionados, K falso o ruptura entre pasado y futuro invalidan la garantía. Si v0, todas diferencias0; degeneración se maneja explícitamente.

## Hipótesis y diseño previos
H1: con K9 y confianza90%, el límite inferior Wilson95% de cobertura en cada celda IID normal/t5 será≥0,85. H2: ninguna muestra cubierta viola el bound de regret a1e−10. No se exige mejor regret medio. Baseline competitivo: chi² sobre toda la muestra y mismo qrobusto, además de plug-in óptimo a s²; reutilizamos sus resultados1nov y datos exactos. El oráculo informado de v tiene regret0 con información extra. Se conserva ruptura temporal como adverso sin garantía. Sensibilidad K1/3/9/30 en n256 es exploración etiquetada, no ajuste de K para declarar éxito.

