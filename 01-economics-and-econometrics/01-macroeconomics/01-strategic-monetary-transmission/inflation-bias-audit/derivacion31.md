# Ciclo31 — Delegación con ambigüedad de varianza

## Pregunta y tres candidatos
¿Puede elegirse q sin fingir conocer σ²? Candidatos: credibilidad endógena (relevante pero cambia juego/instituciones), identificación empírica de α (sin datos/licencia/modelo de medición), minimax regret de varianza (seleccionado: conserva políticas y evaluación social, cierra una brecha concreta y es contrastable con oráculo). Clasificación: adaptación de ingeniería y auditoría de decisión robusta clásica, no descubrimiento disciplinar. Sin distribución subjetiva sobre v.

## Fórmula original, propuesta y unidades
Antes $J(q;v)=A(q)+vB(q)$ con $A=[(q\alpha k)^2+\lambda k^2]/2$, $B=[(q\alpha)^2+\lambda]/[2(1+q\alpha^2)^2]$ y $v=\sigma^2$. Ahora $R(q,v)=J(q,v)-\min_zJ(z,v)$ y elegimos $q_R=\arg\min_{0\le q\le\lambda}\max_{v\in[\ell,u]}R(q,v)$. v tiene unidades de shock²; R es pérdida social normalizada. λ permanece fijo para todos los métodos. La varianza es ambigua para quien nombra al banco, no modifica su reacción óptima tras observar ε; expectativa media sigue qαk.

## Derivación exacta del algoritmo
1. El mínimo de funciones afines en v es cóncavo: $m(v)=\inf_z[A(z)+vB(z)]$. Luego $R(q,v)=A(q)+vB(q)-m(v)$ es convexo en v y su máximo en intervalo compacto está en extremos. No hace falta una malla adversarial para certificar el intervalo.
2. La raíz previa $F(q,v)=qk^2(1+\alpha^2q)^3+v(q-\lambda)=0$ es creciente en q; implícitamente $dq^*/dv=(\lambda-q^*)/F_q\ge0$. Casos degenerados se tratan por convención explícita.
3. Sea $q_\ell=q^*(\ell)\le q_u=q^*(u)$. Fuera de ese intervalo, moverse hacia él mejora ambos extremos. Dentro, $R(q,\ell)$ crece y $R(q,u)$ decrece por el signo de J'.
4. La diferencia continua pasa de no positiva a no negativa. La raíz que iguala regrets minimiza su máximo. Si coinciden pesos extremos se devuelve ese peso. La validez depende de α>0,λ,k≥0 e intervalo finito no negativo, de nuestra pérdida LQ y de nombramiento creíble sin coste. No prueba que minimax regret sea la preferencia correcta de una sociedad real.

