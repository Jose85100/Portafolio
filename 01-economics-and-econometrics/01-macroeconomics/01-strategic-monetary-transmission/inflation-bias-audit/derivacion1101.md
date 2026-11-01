# Ciclo1nov: ¿qué ocurre cuando el intervalo se estima?

## Pregunta, candidatos y línea acumulativa
31oct asumió un intervalo conocido. Comparamos: (a) identificar intervalo con datos macro reales (relevancia alta pero sin modelo de medición/licencia y α no identificado), (b) auditar intervalo estimado bajo un experimento generador explícito (elegido: conecta inferencia a decisión y permite falsar cobertura), (c) ambigüedad conjunta α,v (valiosa pero garantía de extremos aún no demostrada). Aporte: auditoría reproducible de una conexión estadística clásica; no método científico nuevo. El programa mantiene S2 del componente/S1 global.

## Notación, fuente y derivación
Sean observaciones históricas $X_1,\dots,X_n\overset{iid}{\sim}N(\mu,v)$, n≥2, v>0. Estimamos la media para no regalar información: $s^2=\sum_i(X_i-\bar X)^2/(n-1)$. μ y X son shocks normalizados; v,s² son unidades de shock². Bajo normalidad exacta, $Z=(n-1)s^2/v\sim\chi^2_{n-1}$ (NIST). Para nivel c y δ=1−c,
$P(\chi^2_{\delta/2,n-1}\le Z\le\chi^2_{1-\delta/2,n-1})=c$.
Como v y cuantiles son positivos, invertir desigualdades produce
$\ell=(n-1)s^2/\chi^2_{1-\delta/2,n-1}$,
$u=(n-1)s^2/\chi^2_{\delta/2,n-1}$.
No usar directamente `chi2.interval` como intervalo de v: proporciona cuantiles de Z y falta invertir/escalar.

## Adaptación a la API monetaria y propiedades
Original31: $q_R=\arg\min_q\max_{v\in[\ell,u]}R(q,v)$ para extremos conocidos. Propuesta1nov: reemplazarlos por intervalo estimado $C(X)$ y conservar el mismo solver. El dominio previo era v∈[0,16]; intersectamos C con él, asumiendo explícitamente que la verdad pertenece al dominio. Si intersección vacía, abstención, sin forzar valor. La intersección conserva el evento de cobertura para v dentro del dominio; no justifica el dominio a partir de datos. Varianza constante0 tiene pivote degenerado, se trata [0,0]. Overflow produce error.
En el evento $v\in C(X)$, la reducción31 garantiza $R(q_R(X),v)\le B(X)=\max_{z\in C(X)}R(q_R(X),z)$. Bajo IIDnormal y mismo régimen futuro esto tiene cobertura frecuente c. No es P(v∈C observado)=c, ni promesa de pérdida media menor que plug-in. Para colas no normales, correlación o ruptura temporal, la ley pivotal deja de aplicar aunque el código corra. s² tiene invariancia a traslación/permutación y escala cuadrática; las cotas la conservan antes del clipping.

## Diseño fijado antes de interpretar
Config estimada versionada, tres seeds independientes, n16/64/256 y v0,25/1/4;40réplicas por seed/celda;3regímenes. H1(calibración): límite inferior Wilson95% de cobertura IIDnormal agrupada≥0,85 para nominal0,90. H2(ingeniería): cero violaciones del bound en muestras cuyo intervalo cubre verdad a1e−10. No hipótesis de dominancia promedio. Escenario adverso t5 reescalado para varianza v: $X=\sqrt{3v/5}T_5$, pues Var(T5)=5/3. Ruptura: entrenamiento v, futuro4v; el dato futuro jamás entra en ajuste/decisión. Ecuación de pérdida esperada se evalúa exactamente a v futuro: sin ruido de evaluación, no observación empírica fuera de muestra.

