# 03. LGD, EAD y valoración de recuperaciones: modelos de flujo

## 1. LGD como severidad económica descontada

Una LGD contable debe representar déficits de flujos de efectivo coherentes con IFRS 9, no simplemente \(1-\)tasa de recuperación nominal. Una expresión ilustrativa a la fecha de default \(\tau\) es

\[
LGD_\tau=1-
\frac{\sum_{j}R_{\tau+j}(1+r)^{-j/12}
-\sum_j K_{\tau+j}(1+r)^{-j/12}}{EAD_\tau},
\]

con recuperaciones \(R\), costos atribuibles \(K\), tasa pertinente \(r\) y horizonte mensual. La fórmula requiere adaptación para intereses, cobros previos al default, límites de recuperación, garantías, modificaciones y la política de reconocimiento de costos. El déficit de flujos contractual es el objeto contable de referencia; LGD es una parametrización.

Ejemplo: EAD 100; recuperación de 60 en mes 24; costo atribuible 5 en mes 12; tasa efectiva anual 10%. Valor presente neto a default = \(60/1.1^2-5/1.1\approx45.0413\). LGD ilustrativa = \(1-0.450413=54.9587\%\). La LGD nominal basada en recuperación neta de 55 sería 45%; la diferencia refleja el valor temporal del dinero.

## 2. Modelos de recuperaciones

**Workout LGD:** observar recuperaciones a lo largo del tiempo por cohortes de default. Modelar probabilidad de recuperación, monto condicional y tiempo hasta recuperación; la distribución puede ser semicontinua, con masas en cero y uno. Un enfoque hurdle combina:

\[
\Pr(R>0\mid X)=\sigma(X^\top\beta),\quad
R/EAD\mid R>0\sim \mathrm{Beta}(\alpha(X),\beta(X)),
\]

si la razón está estrictamente entre cero y uno. Valores fuera de \([0,1]\), frecuentes por intereses, garantías o recuperaciones superiores a capital, requieren una parametrización distinta, no truncamiento automático.

**Censura:** las cohortes recientes aún no han completado recuperación. Promediar únicamente casos cerrados induce sesgo de selección. Alternativas: modelos de tiempo hasta recuperación, proyección de flujos residuales con incertidumbre y análisis por vintage de default. No usar valores finales conocidos para calibrar modelos destinados a fechas anteriores.

**Garantías:** distinguir valor comercial, valor realizable neto, tiempo de ejecución, prioridad jurídica y costos. Una tasación no es un flujo recuperado.

## 3. EAD para productos amortizables y revolventes

Para un préstamo amortizable, la EAD prevista al default depende del saldo proyectado y de eventos contractuales; para líneas revolventes, de utilización y disposiciones adicionales. Una forma simplificada de credit conversion factor es

\[
EAD_{\tau}=B_t+CCF_{t,\tau}(L_t-B_t),
\]

con saldo dispuesto \(B_t\), límite \(L_t\), y horizonte hasta default \(\tau\). Esta identidad no debe aplicarse si \(L_t<B_t\) o si el límite cambia sin modelarlo. Tampoco debe imponer \(CCF\in[0,1]\) cuando el producto admite intereses, comisiones o sobreutilización que hacen superar el límite; en esos casos se redefine el objetivo.

Para créditos amortizables:

\[
B_{k+1}=B_k(1+r_k)-P_k^{\mathrm{programado}}
-P_k^{\mathrm{prepago}}+D_k^{\mathrm{nuevo}},
\]

donde \(D_k^{\mathrm{nuevo}}\) son disposiciones permitidas. La trayectoria de saldo debe construirse **desde información disponible en el corte** y con supuestos sobre pagos y disposiciones; no insertar saldos observados posteriores como si fueran predicciones.

## 4. Dependencia y wrong-way risk

Si recesión incrementa default, utilización de línea y pérdida por garantía, los tres componentes son dependientes. Para \(D\in\{0,1\}\),

\[
\mathbb E[D\,LGD\,EAD]
=\Pr(D=1)\mathbb E[LGD\,EAD\mid D=1].
\]

Y

\[
\mathbb E[LGD\,EAD\mid D=1]
=\mathbb E[LGD\mid D=1]\mathbb E[EAD\mid D=1]
+\operatorname{Cov}(LGD,EAD\mid D=1).
\]

Omitir la covarianza equivale a una hipótesis restrictiva que debe comprobarse. Un modelo conjunto puede utilizar factor macro común, cópulas, modelos jerárquicos o simulación estructural, con especial atención a identificabilidad y tamaño de muestra.

## 5. Comparación rigurosa de estimadores EAD

Candidatos: saldo al corte proyectado a default, trayectoria contractual ajustada, CCF por segmentos, regresión cuantílica de utilización, modelo de panel con efectos de producto y promedio histórico como baseline. Para cada fecha de observación \(t\) y default futuro \(\tau\), producir \(\widehat{EAD}_{t,\tau}\) sin mirar el futuro; comparar contra \(EAD_{\tau}^{obs}\).

Métricas: error absoluto ponderado por exposición, sesgo \(\sum(\widehat EAD-EAD^{obs})/\sum EAD^{obs}\), calibración por producto/horizonte, pinball loss para cuantiles, intervalos por bootstrap agrupado y desempeño fuera de tiempo. La evaluación condicionada a default es apropiada para precisión de EAD al default, pero debe reconocer sesgo de selección si se generaliza a toda la población.

## 6. Reconciliación contable

Construir un ejemplo unitario donde se conocen calendario contractual, default, recuperaciones, costos y tasa efectiva. Calcular el valor presente de déficits directamente y mediante PD×LGD×EAD. La diferencia debe ser cero dentro de tolerancia cuando ambos métodos codifican los mismos flujos y supuestos. En datos reales, documentar ajustes por intereses, comisiones, prepagos, modificación contractual, saldos fuera de balance y cronología.

## 7. Controles

Trazar fecha de disponibilidad de cada saldo; detectar límites negativos; validar moneda y unidades; controlar doble conteo de recuperaciones; impedir descuentos duplicados; registrar pérdidas fuera de rango y decidir tratamiento contable explícito; separar EAD prevista de EAD observada al default. No declarar superioridad de una ventana de saldo sin backtesting comparativo.
