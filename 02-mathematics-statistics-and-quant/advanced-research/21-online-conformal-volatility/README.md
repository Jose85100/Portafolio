# Online conformal intervals under volatility shifts

**Estado: S2 — prototipo reproducible con simulación sintética; sin validación externa.** Se estudia una pregunta acotada: cuánto tarda una calibración conformal móvil en recuperar cobertura nominal después de un cambio de escala. No se postula una nueva garantía de conformidad para series dependientes.

## Pregunta, hipótesis y criterio

Para observaciones independientes con escala que salta de 1 a 2, ¿una ventana móvil de residuos absolutos mejora la cobertura posterior al cambio frente a una calibración congelada? Hipótesis: con `alpha=0.1`, `window=200` y 20 semillas predefinidas, la cobertura posterior al cambio de la ventana móvil será mayor en promedio que la congelada y conservará anchura finita. Criterio descriptivo preespecificado: diferencia media de cobertura > 0.10 en el escenario 2x; no es prueba de significancia ni evidencia sobre mercados. Escenario 4x es una ablación negativa de severidad. El caso estacionario controla que la adaptación no sea gratuita.

## Método y propiedades

Para puntajes de calibración no negativos `s_1,...,s_m`, el cuantíl split-conformal usa el estadístico de orden `k=ceil((m+1)(1-alpha))`, truncado a `m` cuando la muestra es finita. El intervalo para centro `mu_t` es `[mu_t-q_t, mu_t+q_t]`. La cobertura marginal finita usual requiere intercambiabilidad entre calibración y observación futura; el orden de los rangos es uniforme bajo intercambiabilidad, dando cobertura al menos `1-alpha` sin supuestos paramétricos. Tras el cambio, las observaciones antiguas no son intercambiables con las nuevas, por lo que esa garantía deja de aplicar.

La actualización móvil elimina el puntaje más antiguo e incorpora el más reciente. El invariante computacional es `lower <= upper`; el cuantíl siempre es un valor observado no negativo. Al congelar la ventana en una región estacionaria, el estimador empírico converge al cuantíl poblacional bajo la ley de grandes números (para una ventana que crece); para ventana fija no afirmamos consistencia asintótica. En el modelo normal centrado, el oráculo es `q*=Phi^-1(1-alpha/2)*sigma`; la comparación principal usa calibración conformal congelada como baseline empírico.

## Reproducibilidad

Python 3.10+, NumPy, Matplotlib y nbformat. Un único comando desde esta carpeta: `python run_study.py`; `make check` ejecuta pruebas y luego genera resultados. Configuración y semillas están en `config.json`. Salidas: `results/raw_series.csv` (series sintéticas completas), `summary.csv`, `summary.json`, `sensitivity.csv` (ventana 50–400), `calibration_size.csv` (n=20–400 en estacionariedad), `scale_break.png` y `notebook.ipynb`. El runner ejecuta en orden todas las celdas Python del notebook con el intérprete local y guarda salidas reales y contadores. El kernel Jupyter no pudo abrir sockets TCP/IPC en este sandbox; por eso el notebook usa un ejecutor en proceso y deja esa limitación en metadata. Las métricas se calculan a partir de simulaciones recién generadas; no son observaciones históricas.

En las 20 réplicas, el escenario 2x arroja cobertura posterior media 0.588 para el umbral congelado y 0.881 para el móvil; el oráculo gaussiano de escala conocida alcanza 0.897. En el escenario estacionario fijo y móvil quedan en 0.900 y 0.901 respectivamente. El negativo 4x muestra el costo claro: el móvil llega a 0.871 con ancho medio 8.42 frente a 0.317 y ancho 3.33 del fijo. El método móvil recupera cobertura ampliando mucho la banda, y aun así no llega exactamente a nominal durante el transitorio. Desviaciones estándar entre las semillas son descriptivas, no intervalos inferenciales.

## Estructura

- `src/online_conformal.py`: cuantíl, intervalo, simulador y evaluación, con anotaciones de tipos.
- `tests/`: extremos, cuantíl, semilla, invariantes y respuesta al cambio.
- `informe14p.md`: manuscrito de investigación dividido en catorce páginas editoriales.
- `prior_art.md`: cribado inicial de literatura y distinción de contribución.
- `roadmap.md`: experimentos que faltan antes de una afirmación operacional.

## Riesgos y alcance

Simulaciones iid gaussianas omiten autocorrelación, colas pesadas, estimación del centro, datos faltantes y cambios graduales. La ventana móvil reacciona con demora de hasta aproximadamente el tamaño de ventana y puede empeorar cobertura si la escala vuelve rápidamente. La implementación usa cuantíl de ventana y no incorpora garantías de cobertura online bajo dependencia/arbitrariedad. No usar como intervalo de riesgo financiero ni para decisiones de capital.
