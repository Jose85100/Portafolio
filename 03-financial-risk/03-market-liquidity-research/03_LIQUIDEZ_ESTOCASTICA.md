# 03. Liquidez estocástica: probabilidad de déficit y tiempo de supervivencia

## Problema
La liquidez de financiación se relaciona con la capacidad de atender pagos a su vencimiento sin pérdidas inaceptables. La métrica determinista de gap por bandas no representa la incertidumbre de flujos, renovación de fondeo ni llamadas de margen.

## Modelo discreto
Sea \(C_t\) caja disponible, \(I_t\) entradas realizables, \(O_t\) salidas contractuales y comportamentales, \(F_t\) fondeo adicional ejecutable, y \(M_t\) llamadas de margen:

\[
C_{t+1}=C_t+I_t-O_t+F_t-M_t.
\]

Defina \(\tau=\inf\{t\ge1:C_t<0\}\), tiempo de primer déficit. La probabilidad de ruptura a horizonte \(H\) es \(\Pr(\tau\le H)\); el tiempo de supervivencia es \(\min(\tau,H)\) bajo censura administrativa. La caja negativa es un criterio ilustrativo; en operación deben incorporarse colchones mínimos, restricciones de moneda, elegibilidad de activos, haircuts y cut-offs intradía.

## Dependencia de flujos
Modelar salidas \(O_t=\bar O_t+\lambda_U U_t+\lambda_R R_t+\varepsilon_t\), con \(U_t\) desempleo/actividad y \(R_t\) riesgo reputacional o concentración de depósitos. Para entidades sin depósitos, sustituir retiros por vencimientos de deuda, no renovación de líneas y cobros insuficientes. Los parámetros son específicos de negocio.

Para una aproximación continua,

\[
dC_t=\mu_t\,dt+\sigma_t\,dW_t-dJ_t,
\]

donde \(J_t\) representa saltos de salida. Una difusión browniana permite saldos negativos y no modela discrecionalidad de fondeo; la interpretación correcta es proceso de caja neta, no cantidad física de efectivo.

## Resultados
Estimar \(p_H=N^{-1}\sum_{b=1}^N\mathbf1\{\tau_b\le H\}\), intervalo binomial o bootstrap por escenarios dependientes, distribución de déficit máximo y Expected Shortfall de déficit acumulado. Para eventos muy raros, Monte Carlo ingenuo puede ser ineficiente; importance sampling requiere corrección de likelihood ratio.

## Validación
Confrontar pronósticos de entradas/salidas con realizaciones, errores por plazo y concentración, supuestos de renovación, días con fricción operativa y accesibilidad real de activos líquidos. LCR y NSFR son indicadores normativos con definiciones precisas; esta simulación no calcula automáticamente ninguno de ellos.

## Pregunta económica
¿Cuándo un balance aparentemente solvente puede entrar en déficit por descalce temporal y comportamiento correlacionado? La probabilidad de déficit no es probabilidad de insolvencia; ambas se relacionan pero no son equivalentes.
