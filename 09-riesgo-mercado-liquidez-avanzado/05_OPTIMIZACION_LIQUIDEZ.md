# 05. Optimización CVaR con restricciones de liquidez y costos de mercado

## Objetivo
Seleccionar pesos de activos y plan de liquidación que equilibren rentabilidad, riesgo extremo y ejecutabilidad. Una cartera de baja volatilidad puede ser inviable si no puede liquidarse durante una crisis.

## CVaR como problema convexo
Para pérdidas por escenario \(L_s(w)=-r_s^\top w\), probabilidades \(p_s\), confianza \(\alpha\), la formulación de Rockafellar–Uryasev es

\[
\min_{w,\eta,u_s}\ \eta+\frac{1}{1-\alpha}\sum_s p_su_s
\]

sujeto a \(u_s\ge L_s(w)-\eta,\;u_s\ge0,\;\sum_iw_i=1,\;w_i\ge0\), y límites de concentración. Con pérdidas afines y conjunto factible convexo, el problema es convexo (lineal en esta representación). El minimizador de \(\eta\) corresponde a un cuantil óptimo; el objetivo óptimo corresponde a CVaR/ES de la distribución discreta.

## Costos de liquidación
Sea \(q_i\) cantidad a vender y \(V_i\) volumen disponible. Una función ilustrativa de impacto temporal es

\[
C_i(q_i)=a_i|q_i|+b_i\frac{q_i^2}{V_i},
\qquad a_i,b_i\ge0,\ V_i>0.
\]

Para \(q_i\ge0\), es convexa. Puede añadirse a cada pérdida por escenario si la liquidación es parte del horizonte modelado. La convexidad puede perderse con impacto endógeno cruzado, restricciones discretas o decisiones estratégicas.

## Restricciones
\[
\sum_i p_i^{\mathrm{venta}}q_i-C(q)\ge G,\quad
0\le q_i\le\min(H_i,\kappa_i V_i),
\]
donde \(G\) es gap de caja. **Atención:** la restricción de recaudación neta \(\sum pq-C(q)\ge G\) es supernivel de una función cóncava y por tanto convexa cuando \(C\) es convexa y precios exógenos; con precios dependientes de ventas puede cambiar la geometría.

## Robustez
Incertidumbre en retornos, correlaciones, spreads y profundidad: considerar conjuntos robustos \(\mathcal U\) y minimizar \(\max_{\theta\in\mathcal U}CVaR_\alpha(w;\theta)\). Un conjunto de incertidumbre demasiado grande genera soluciones excesivamente conservadoras; evaluar costo de robustez y desempeño fuera de muestra.

## Validación
Comparar Markowitz, mínima varianza, CVaR sin costos y CVaR con costos. Backtest con ventanas rodantes, slippage realista, límites de participación y escenarios de suspensión. Reportar utilidad económica neta, no solo Sharpe bruto. Evitar look-ahead en retornos y liquidez estimados.
