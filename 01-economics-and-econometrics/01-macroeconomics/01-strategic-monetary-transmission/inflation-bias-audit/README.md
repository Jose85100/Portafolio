# Auditoría acumulativa de sesgo inflacionario y delegación

S2 del componente estático; programa general S1. Ciclo29 se conserva y ciclo30 extiende el mismo código con delegación conservadora. No evidencia empírica ni teoría nueva.

## Reproducir

Desde esta carpeta: `bash run.sh`. Requiere Python3.11+, venv y acceso a PyPI para dependencias fijadas. Instala, ejecuta tests/cobertura/lint/tipos, reproduce ambos experimentos y notebook narrativo con outputs visibles. Alternativa contenedor: usar imagen Python3.11, copiar carpeta, ejecutar el mismo comando; no imagen certificada.

`results/delegation.csv`, `delegation-summary.json`, `delegation.png` y `notebook.ipynb` contienen evidencia nueva. `results/cases.csv` y comparación anterior conservan baseline29. Fórmulas, unidades, sensibilidad y controles negativos están explicados en notebook e informe. `delegation-config.json` registra malla, fuente sintética y seed no aplicable; versiones fijadas en requirements y registradas por experimento anterior. Baseline justo: misma pérdida social λ y mismos shocks; solo cambia peso delegado q. Tres ideas, matriz prior art y clasificación de aporte en informe. No contrato institucional implementado, no estimación/calibración, no agentes heterogéneos o Markov.

## Ciclo31 — varianza ambigua

Mismo `bash run.sh`: ahora reproduce también `src.run_ambiguity`. Artefactos `results/ambiguity.csv`, `ambiguity-runtime.csv`, `ambiguity-summary.json`, `ambiguity.png`, derivacion31.md y prior-art31.md. 144regímenes exactos;81mejoras63empates en peor regret frente a plug-in. Mayor coste y pérdida de optimalidad puntual explícitos. Ver informe ciclo31 y notebook acumulativo.

## Ciclo1nov — intervalo estimado y fallo temporal

Mismo `bash run.sh`: añade `src.run_estimated_interval`,3240réplicas en3regímenes. `results/estimated-interval.csv`, `estimated-shocks.csv.gz`, `estimated-interval-summary.json`, `estimated-interval-aggregate.csv`, `estimated-interval-runtime.csv`, `estimated-interval.png`. Derivación en derivacion1101.md/notebook,fuentesenprior-art1101.md,contratoen data-contract1101.md. CoberturaIIDnormal90,46%; ruptura temporal sin cobertura a n64/256. No evidencia macroreal ni dominancia promedio.

## Ciclo2nov: cobertura bajo cuarto momento acotado

Mismo `bash run.sh`, añade `src.run_moment_interval`. Reutiliza los fixtures1nov porhash. `moment-config.json`, `derivacion1102.md`, `prior-art1102.md`; CSV/JSON y `results/moment-interval.png` muestran cobertura, amplitud y coste decisorio. K9 es un supuesto externo, no estimación de kurtosis. Cobertura t5 mejora a costa de intervalos amplios y mayor regret medio; ruptura temporal sigue sin garantía.

## Ciclo3nov: dependencia estacionaria AR(1)

El mismo `bash run.sh` añade `src.run_dependent_interval` y genera `notebook-dependent.ipynb`. El incremento compara (i) intervalo Chebyshev del promedio de diferencias cuadradas, con covarianza exacta bajo Gaussianidad conjunta, (ii) GLS chi-cuadrado exacto con rho conocido y (iii) intervalo iid mal especificado como control negativo. Los seeds `[1103,1104,1105]`, 30 réplicas por seed/celda y ocho combinaciones n/rho están en `dependent-config.json`. Dos celdas no alcanzan el límite Wilson95 predefinido para el baseline GLS; ese resultado negativo no refuta su pivote exacto y permanece visible en `informe1103.md`. Datos sintéticos únicamente; detalle de derivación, fuentes y límites en `derivacion1103.md` y `prior-art1103.md`.
