# Derivación y fronteras del cálculo

## Primer default y supervivencia

Sea h_m=P(T=m | T≥m), S_0=1, S_m=∏(1−h_j). Entonces q_m=S_(m−1)h_m y F_H=Σq_m=1−S_H. Nunca sumar hazards como PD lifetime. La conversión de p12 bajo hazard constante es h=1−(1−p12)^(1/12). Para supervivencia discreta se maximiza Σ[y log h+(1−y)log(1−h)] sobre filas en riesgo, no sobre todos los meses de todos los clientes incluyendo posteriores al default.

En Markov, una distribución π se propaga como πP. La probabilidad acumulada de default es su última componente. La masa mensual nueva es π_vivos P_vivos,default; el stock ya absorbido no se cuenta otra vez. El cambio de odds de default por macro vuelve a escalar las probabilidades de destinos vivos, conservando suma uno.

## Descuento y horizonte

Para escenario s:

$$ ECL_{i,s}^{(K)}=\sum_{m=1}^{K}q_{i,m,s}\,LGD_{i,m,s}^{default}\,EAD_{i,m,s}\,(1+EIR_i)^{-m/12}. $$

Stage 1: K=min(12, vida contractual). Stage 2: K=vida contractual. LGD a default puede contener flujos de recuperación después de K: **el corte es de eventos de default, no de recuperaciones**. La aproximación ubica el default al fin del mes y usa EAD al inicio: es una convención conservadora de discretización, no exactitud intramensual. Debe probarse convergencia con pasos menores si la precisión temporal es material.

LGD por flujo:

$$ LGD^{default}=1-\sum_j R_j^{neto}(1+EIR)^{-\Delta_j}/EAD. $$

El factor (1+EIR)^(-Δ_j) va de recuperación a default; el de ECL va de default a reporte. Para un default con probabilidad p en un año y recuperación fracción r dos años después, la pérdida a reporte es p·EAD·[1−r/(1+EIR)²]/(1+EIR). Esta identidad se prueba contra la valoración directa de dos cashflows.

## LGD fraccional y CCF

El logit fraccional usa μ=σ(Xβ) y minimiza media[log(1+exp(Xβ))−yXβ]+λ||β_sin_intercepto||²/2. No interpreta y como una realización binaria; usa cuasiverosimilitud para la media condicional. Features estandarizadas con entrenamiento; endpoints válidos. Las predicciones quedan en [0,1], una restricción que debe cambiarse para pérdidas o disposiciones que puedan superar límites.

## Prepago y exposición

La anualidad satisface B_(m+1)=max(B_m(1+r_mes)−cuota,0), con cuota calculada por vida remanente. El prepago total independiente agrega retención (1−CPR)^((m−1)/12). Se evalúa el saldo esperado incluyendo cierre por prepago, condicionado a no default previo; no se multiplica otra vez por S_default. Default y prepago dependientes necesitan riesgos competitivos, todavía no implementados.

## Escenarios y dependencia

ECL=Σ_s w_sECL_s, w_s≥0, Σw_s=1. No es equivalente a evaluar los componentes al macro promedio. La información pública de IFRS Foundation [sobre escenarios](https://www.ifrs.org/news-and-events/news/2016/07/25-webcast-on-ifrs-9/) trata consistencia, no linealidad y SICR prospectivo; no define pesos universales. Aquí .6/.3/.1 y el factor macro son supuestos de referencia, no un pronóstico de Colombia.

Los componentes comparten macro, capturando dependencia por escenario. No se estima la covarianza residual entre LGD y EAD condicional a default; producto de medias dentro del escenario es otra hipótesis. No se incorporan overlays sin trazabilidad ni se cambian pesos para alcanzar una provisión deseada.

## Activos deteriorados y matriz simplificada

Stage 3 financiado: saldo bruto menos PV de recuperaciones netas desde reporte, con piso cero en esta interfaz. La ruta excluye PD futura. La matriz simplificada es una tasa de shortfall lifetime por cohortes de cuentas por cobrar; debe usarse sólo para instrumentos elegibles y sin superponer resultados para la misma exposición.

## Fuentes y alcance

- IFRS Foundation, [Forward-looking information and multiple scenarios, 2016](https://www.ifrs.org/news-and-events/news/2016/07/25-webcast-on-ifrs-9/): material público de implementación, no reemplaza el estándar.
- Botha y Verster, [tutorial de supervivencia discreta, 2025](https://arxiv.org/abs/2507.15441): referencia metodológica; no se copia su base de datos ni se replica su estudio.
- Documentos 01–06 de esta carpeta: marco conceptual ampliado. Las ideas allí formuladas no se consideran implementadas salvo correspondencia explícita con código, tests y notebooks.

No se declara cumplimiento integral de IFRS 9: quedan fuera clasificación/medición, coberturas, POCI, modificaciones, curas, asientos, interés sobre saldo neto, revelaciones IFRS 7 y provisión prudencial SFC. La elegibilidad y la política contable requieren revisión independiente.
