# Streaming moments — auditoría de cancelación (29 octubre2026)
Prototipo reusable Python, varianza escalar ddof0/1 por Welford desplazado y fusión Chan. Algoritmos clásicos; aporte incremental: particiones, oráculo Decimal de entradasfloat y controles de pérdida de representación.

Desde esta carpeta: `bash run.sh`. Crea entorno `.venv`, instala versiones directas fijadas, ejecuta tests, cobertura del núcleo, Ruff, mypy del núcleo, benchmark y notebook. Requiere Python3.12, pip e internet para instalación. Alternativa `MATH_ENV=/ruta/venv bash run.sh`. Dependencias transitivas no bloqueadas; sin Docker.

Salida: `results/raw.csv`(40filas), `results/summary.json`, `results/audit.png`, logs y notebook.ipynb ejecutado secuencialmente con IPython en proceso(namespace nuevo), sin afirmar kernel separado. Configuración en config.json, fuentes verificadas en fuentes.md y referencias.bib. Informe crítico en informe.md.

API: `from src.moments import summarize`; `summarize(iterable).variance(ddof=0)`. `Moments.merge` combina estados válidos originados por API; constructor interno es confiado, no validador de estados arbitrarios. Un solo pase, estado O(1); no materializa iterable. El benchmark sí materializa datos y usa oráculo costoso. No soporta pesos, NaNs, complejos, overflow extremo ni paralelización real. Fusión asociativa en reales, sólo aproximada en float64. Intervalos estadísticos y modelo financiero fuera de alcance. No modifica EL83 ni tolerancia1e-10 compartida.

Madurez: prototipo matemático acotado, ejecutado; no promoción de programas advanced-research ni equivalencia automática S2/M2. Revisión independiente se registra en PR.

## Extensión acumulativa30: escala externa y estados de rango
`bash run.sh` ahora reproduce29 y30; resultados29 se regeneran, sin borrar sus fixtures. `scaled_moments(iterable, exponent, ddof=0)` en src/scaled.py usa el mismo núcleo29 con unidad2^e declarada. Devuelve varianza y SD físicas por separado: puede devolver SDfinita con variance=None y status variance_overflow/variance_underflow. Estado std_overflow si SD tampoco cabe. Escala mala: normalization_failure; n cuenta observaciones procesadas hasta fallo, no cardinalidad total del iterable. No consumir remanente tras rechazo.

Cada valor normalizado no nulo debe estar entre2^-400 y2^400 (ventana conservadora de esta API, no teorema de estabilidad). Mezclas de rango excesivo pueden rechazarse; no escala automática. Consultar notebook_scale.ipynb didáctico ejecutado, config_scale.json, results/scale_* y informe_scale.md con14p. Priorart/atribución en prior_art.md; log y roadmap acumulativos en RESEARCH_LOG.md. Sin lenguaje adicional: wrapperPython es suficiente y evita un contrato multilenguaje ficticio. EL83 intacto.
