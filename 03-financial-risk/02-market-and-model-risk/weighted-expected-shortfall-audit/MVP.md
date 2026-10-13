# MVP: auditoría de Expected Shortfall ponderado

**Qué es:** motor de VaR inversa-CDF y ES por masa de cola fraccionaria para distribuciones finitas con pesos, acompañado de un oráculo LP, tres baselines reales del repo y una ablación de cola estricta.

**Cómo se corre:** desde esta carpeta, `bash run.sh` (Python 3.12, venv y pip; internet para instalación inicial).

**Qué produce:** pruebas con cobertura del núcleo, lint y tipos, 320 distribuciones × cinco métodos = 1.600 filas crudas, 98 mediciones de rendimiento, figura PNG, metadatos, notebook ejecutado. Falla si error máximo contra LP excede 1e-8.

**Qué NO cubre:** calibración de pesos, predicción, backtesting de ES, estimación de capital regulatorio, migración de baselines existentes, C++ nuevo ni datos reales. El contrato de reproducción requiere el repositorio completo porque carga sus baselines.

**Madurez:** prototipo validado numéricamente en escenarios sintéticos; no producción. La fórmula es prior art, no novedad teórica.
