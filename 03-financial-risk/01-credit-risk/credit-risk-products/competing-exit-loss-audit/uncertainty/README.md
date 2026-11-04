# Incertidumbre de LGD condicionada al default (extensión del audit)

Pregunta: ¿qué riesgo de pérdida desaparece cuando se sustituye la LGD incierta por una estimación puntual? Esta extensión integra exactamente los dos primeros momentos de EAD lineal en el tiempo de default de riesgos competidores, multiplicados por LGD~Beta independiente. Es adaptación analítica de fórmulas conocidas, no modelo calibrado ni contribución científica original.

La línea acumulativa ya separa masa/default-prepago, fechas y disponibilidad, EAD×LGD afines. Hoy se añade la incertidumbre condicional de severidad sin modificar el contrato anterior. Tres candidatos: (1) Beta-LGD y momentos exactos (elegido: cerrado analíticamente y sin datos); (2) LGD dependiente de tiempo/default (aplazado: falta estimación/identificación); (3) recuperaciones censuradas y modelo de workout (aplazado: faltan datos autorizados y proceso de censura).

## Fórmula y supuestos

Para hazards constantes λd, λp, h=λd+λp, horizonte T y EAD(t)=a+bt, la densidad incondicional de default es λd exp(−ht), 0≤t≤T. Condicionalmente, G~Beta(α,β), independiente de Tdefault. Entonces

\[
E[L]=E[G]\,\lambda_d\int_0^T e^{-ht}(a+bt)dt,
\quad E[L^2]=E[G^2]\,\lambda_d\int_0^T e^{-ht}(a+bt)^2dt.
\]

\(E[G]=α/(α+β)\), \(E[G²]=α(α+1)/[(α+β)(α+β+1)]\), \(Var(L)=E[L²]-E[L]^2\). Integrales t^k e^{-ht} para k=0,1,2 se calculan en forma cerrada; la función maneja h=0 como límite. P(L=0) incluye no-default y prepago. Supuestos: EAD no negativa y lineal; hazards constantes; LGD Beta independiente del tiempo de default y de prepago; pérdida undiscounted. No representa IFRS9/ECL, downturn LGD, colateral, recuperaciones, costos ni calibración.

El baseline plug-in fija G=E[G], por lo que conserva varianza temporal de default pero elimina varianza de severidad: su varianza no puede superar la completa bajo independencia. La diferencia positiva es una auditoría de incertidumbre omitida, no mejora predictiva.

## Reproducir

Desde esta carpeta: `bash run.sh`. Requiere Python 3.10+; librería núcleo sólo stdlib; matplotlib/numpy se usan para figura. Config determinista en `benchmarks/config.json`; no hay dataset ni semilla porque el benchmark es cuadratura/modelo analítico. Produce `results/summary.json`, `comparison.csv`, `run_metadata.json`, `lgd_uncertainty.png`. La tabla compara beta variable con plug-in a media constante. El script verifica esperanza vs Simpson compuesto n=4096.
