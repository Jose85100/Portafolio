# Contrato del MVP — programa 04

**Qué es:** benchmark bivariado de coexcedencias, identidad de Kendall tau y reducción de varianza condicional. S1→S2 limitado a parámetros conocidos, no al programa entero de geometría extrema. Base revisada: `2eb24941cd7fd7fd31a9bad05670a25361574413`. Fecha: 2026-10-18.

**Cómo corre:** `make run` desde esta carpeta; Python 3.12 + make + venv + internet para dependencias. El comando instala y reproduce lint, formato, mypy, tests, simulación, informe y notebook ejecutado. README documenta entorno y alternativa de intérprete.

**Qué produce:** 48 comparaciones de cuadratura, 1.280 corridas (80 réplicas por celda), tres muestras de verificación de Kendall, CSV/JSON, tiempos y memoria rastreada, figura, muestras NPZ, cobertura, ocho celdas de notebook con outputs, informe crítico y checklist. Falla si un umbral predefinido no pasa. No exige identidad de tiempos entre máquinas.

**Baselines:** cópula gaussiana frente a t4/t30 con igual rho y tau poblacional; simulación directa frente a condicional a igual N; dos coordenadas de cuadratura y controles gaussianos independientes. Sin ocultar ceros, denominadores indefinidos ni sobrecostes.

**Qué NO cubre:** estimación o selección de cópulas, incertidumbre paramétrica, series dependientes, asimetría, dimensión alta, aplicación pública financiera, validación de VaR/ES/capital. No se afirma novedad de la t-cópula ni del Monte Carlo condicional. No se toca quant-libraries/EL=83 ni se reemplaza el motor de cartera de riesgo.

**Evidencia de cierre:** `benchmarks/checklist.json`, `tests.txt`, `coverage.json`, `results.json`, artefactos y workflows. La revisión visual completa del notebook se distingue de ejecución y validación estructural.
