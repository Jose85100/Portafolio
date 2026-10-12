# 01. Fundamentos: medición de pérdidas crediticias esperadas

## 1. Objeto de medición

El deterioro bajo IFRS 9 es una medición prospectiva de **déficits de flujos contractuales**: diferencia entre flujos contractualmente exigibles y flujos que la entidad espera recibir, descontados con la tasa pertinente. Para compromisos de préstamo y garantías financieras existen particularidades de exposición y flujos. Una ECL debe reflejar un importe imparcial y ponderado por probabilidad, valor temporal del dinero e información razonable y sustentable sobre pasado, condiciones presentes y pronósticos futuros disponible sin costo o esfuerzo desproporcionado.

La ecuación fundamental es una expectativa de flujos descontados:

\[
ECL_t=\mathbb E_t\left[\sum_{u>t}D(t,u)\big(C_u-R_u\big)\right],
\]

donde \(C_u\) representa flujos contractuales relevantes, \(R_u\) cobros esperados y \(D(t,u)\) factores de descuento coherentes con la tasa efectiva aplicable. Esta escritura compacta requiere tratamiento correcto de vencimientos, prepagos, reestructuraciones, costos de recuperación, garantías y cronología de cobros. El déficit puede no ocurrir exclusivamente al momento de default.

La representación operativa por componentes

\[
ECL_t\approx\sum_{s=1}^{S}w_s\sum_{k=1}^{H}
DF_{t,k,s}\,\Delta PD_{t,k,s}\,LGD_{t,k,s}\,EAD_{t,k,s}
\]

es una **aproximación condicionada a supuestos**. Exige consistencia entre la definición de default, EAD al default, LGD como pérdida descontada, distribución de tiempos de default, escenarios y flujos. Si LGD y EAD son estocásticas y dependen del evento de default, la forma correcta es

\[
ECL_t=\sum_{s,k}w_s\,DF_{t,k,s}\,
\Pr(T=k\mid s,\mathcal F_t)\,
\mathbb E[LGD_k EAD_k\mid T=k,s,\mathcal F_t].
\]

En general, \(\mathbb E[LGD\cdot EAD\mid D]\neq \mathbb E[LGD\mid D]\mathbb E[EAD\mid D]\). Factorizar sin evaluar la covarianza puede sesgar la estimación.

## 2. Supervivencia y PD marginal

Sea \(h_k=\Pr(T=k\mid T\ge k,\mathcal F_t)\) la hazard discreta. Entonces

\[
S_0=1,\quad S_k=\prod_{j=1}^k(1-h_j),\quad
\Delta PD_k=S_{k-1}h_k.
\]

**Demostración:** \(\Pr(T=k)=\Pr(T\ge k)\Pr(T=k\mid T\ge k)=S_{k-1}h_k\). La suma telescópica satisface \(\sum_{k=1}^H\Delta PD_k=1-S_H\). No sumar PD acumuladas por periodo: se duplicaría la probabilidad de default.

## 3. Horizontes contables y económicos

La asignación general de Stage 1 es ECL de 12 meses; Stage 2 y Stage 3 requieren ECL durante la vida esperada pertinente. **ECL de 12 meses no equivale a 12 meses de déficits de caja:** corresponde a pérdidas de vida que surgen de defaults posibles durante los siguientes 12 meses. El horizonte de vida debe considerar las condiciones contractuales y las excepciones pertinentes, particularmente ciertas facilidades revolventes donde la exposición al riesgo no queda adecuadamente limitada por el periodo contractual de cancelación.

No debe aplicarse un único horizonte de 12 meses a todas las recuperaciones. Una exposición que incumple dentro de los 12 meses puede recuperarse años después; la LGD debe reflejar esos flujos y su descuento.

## 4. Descuento y coherencia temporal

Para una tasa efectiva anual \(r\) y periodos mensuales, un descuento ilustrativo es \(DF_k=(1+r)^{-k/12}\). En un modelo de recuperaciones, cada cobro se descuenta desde su fecha de realización al punto de medición correspondiente; mezclar tasas nominales y efectivas, o descontar dos veces una LGD ya expresada en valor presente, genera error sistemático. Las reglas exactas de descuento dependen del instrumento (incluidos activos credit-impaired originados o adquiridos) y deben documentarse.

## 5. Propiedades y pruebas

Con pérdidas no negativas, \(ECL\ge0\). Bajo exposición y severidad fijas, aumentar una PD marginal sin cambiar el resto incrementa ECL. Bajo factores de descuento positivos y flujos de recuperación idénticos, desplazar recuperaciones hacia fechas posteriores no disminuye el déficit descontado. La monotonicidad respecto de una variable macro no está garantizada sin supuestos sobre PD, EAD, LGD y su dependencia.

Controles obligatorios: \(0\le h_k\le1\); \(\sum\Delta PD_k\le1\); escenarios \(w_s\ge0,\sum w_s=1\); igualdad de moneda y fecha; conciliación de exposición contable; identidad entre pérdida por cash shortfalls y cálculo por componentes en un caso de prueba controlado.

## 6. Ejemplo analítico

Crédito bullet con EAD 100, default únicamente al final del primer año con probabilidad 4%, LGD ya descontada de 45% y sin otros déficits. ECL = \(100(0.04)(0.45)=1.8\). Si la LGD de 45% fuese **no descontada** y la pérdida se materializara en un año, con tasa efectiva del 10%, el resultado ilustrativo sería \(1.8/1.10\approx1.6364\). Estos dos resultados **no** pueden mezclarse: la definición de LGD determina dónde se aplica el descuento.

## 7. Riesgos de implementación

Errores comunes: usar PD acumulada como marginal; tomar saldo de default realizado como variable predictora ex ante; promediar LGD sin ponderación por exposición; usar escenarios macro que no suman uno; duplicar descuento; excluir contratos cancelados del histórico y generar sesgo de supervivencia; confundir provisión IFRS 9 con provisión prudencial. Ninguna simplificación se acepta sin cuantificar materialidad y sesgo.
