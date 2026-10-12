# 06. Stress testing conjunto de mercado y liquidez

## Motivación
La caída de precio de activos puede reducir caja disponible por haircuts, aumentar requerimientos de margen, limitar acceso a fondeo y obligar a vender a spreads crecientes. Modelar riesgo de mercado y de liquidez por separado puede subestimar su interacción.

## Vector de estado
\[
X_t=(P_t,\Sigma_t,C_t,H_t,M_t,F_t),
\]
con precios, volatilidad, caja, haircuts, márgenes y acceso a financiación. Un modelo de simulación discretizado:

\[
\log P_{t+1}=\log P_t+\mu_{S_t}\Delta t+
\sigma_{S_t}\sqrt{\Delta t}\,\varepsilon_{t+1}-I(q_t),
\]
\[
C_{t+1}=C_t+\mathrm{inflows}_t-\mathrm{outflows}_t
-\mathrm{margin}_t+\mathrm{funding}_t+\mathrm{sales}_t.
\]

El término \(I(q_t)\) exige unidad coherente (impacto sobre log-precio, no sobre precio absoluto). Las decisiones \(q_t\) deben cumplir restricciones de inventario, velocidad de venta y colateral. Para valorar derivadas se requiere modelar exposición y márgenes de forma específica.

## Arquitectura de escenarios
- Shock de tasas: curva completa, duración/convexidad, repricing y basis risk.
- Shock de FX: exposiciones netas, coberturas, descalces de moneda y collateral FX.
- Shock de spread: mark-to-market, haircut, concentración y repo.
- Shock de liquidez: no renovación de líneas, mayores retiros, bid–ask y caída de profundidad.
- Shock conjunto: correlaciones condicionales, saltos y transición a régimen de crisis.

Los escenarios deben preservar restricciones económicas y contables, pero permitir rupturas plausibles de correlaciones históricas. Un stress severo no debe recibir peso de probabilidad arbitrario para convertirlo en pérdida esperada contable.

## Métricas
Distribución de P&L, VaR/ES, probabilidad de déficit de caja por horizonte, tiempo al primer déficit, mayor gap acumulado, costos de liquidación, fracción de inventario liquidada y capacidad de supervivencia por moneda. Distinguir riesgo de liquidez intradía de liquidez estructural.

## Atribución de interacciones
Si \(L(A,B)\) es pérdida bajo shock de mercado \(A\) y de liquidez \(B\), interacción:

\[
I_{AB}=L(A,B)-L(A,0)-L(0,B)+L(0,0).
\]

Un \(I_{AB}>0\) indica amplificación supra-aditiva en ese experimento; no implica causalidad identificada ni universalidad del resultado. Puede atribuirse con valores de Shapley para múltiples shocks, declarando dependencia del conjunto de coaliciones.

## Evaluación crítica
La liquidez de mercado se evapora endógenamente, los agentes reaccionan a la política de liquidación y la distribución de crisis no se identifica bien con muestras normales. Los modelos deben acompañarse de reverse stress testing: buscar el shock mínimo que viola un umbral operativo. Documentar supuestos, errores de aproximación, límites regulatorios y decisiones de gestión.
