# Contrato del MVP — programa 05

**Qué es:** auditoría del filtro discreto `(1-L)^d` y su truncación causal, no un detector de memoria larga. S1→S2 limitado a este operador. Fecha 2026-10-19. Base revisada: `dd5dc42984ca98ecf3ccda47a21dfd4008afe0bb`.

**Cómo corre:** `make run` en esta carpeta; Python 3.12, make, venv y acceso a PyPI. README documenta entorno, instalación, reproducción y qué archivos se regeneran.

**Qué produce:** 36 escenarios sintéticos, seis métodos (216 resultados), 648 tiempos crudos, seis comparaciones de alta precisión, 12 entradas NPZ, salidas seleccionadas, CSV/JSON, figura, tests/cobertura, ocho celdas de notebook ejecutadas, informe crítico y checklist. La ejecución falla si no pasa un umbral fijado en config.json. Los tiempos no son invariantes entre máquinas.

**Baselines:** convolución directa completa, FFT lineal completa, rezagos fijos 32/128, corte por primer coeficiente omitido ≤.001 y selector de masa de cola ≤.01. La FFT circular sin relleno es una ablación deliberadamente incorrecta, no un competidor calibrado.

**Qué NO cubre:** inferencia de d/Hurst, clasificación memoria larga versus rupturas, datos reales, ARFIMA estimado, Caputo, EDE fraccionales, órdenes fuera de [.01,.99], prehistoria desconocida, streaming o validación financiera. No se reclama novedad de diferenciación fraccional, de FFT ni de la desigualdad triangular.

**Cierre:** src, comando único, tests, baseline con números, salida cruda/figura, README/informe/BibTeX/MVP y notebook ejecutado. Evidencia detallada en benchmarks/checklist.json y logs. No se modifica quant-libraries ni su contrato EL=83.
