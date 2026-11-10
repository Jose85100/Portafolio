# MVP y nivel de madurez

**MVP de investigación reproducible.** El paquete define la atribución de ES de una distribución finita y ejecuta una prueba de concepto con tres componentes de pérdida sintéticos, un baseline prorrata de ES standalone, ablación a promedio simple y ablación adversa que quita el estado de crisis. Incluye CSV/JSON de escenarios y métricas, figura, notebook con outputs del experimento, pruebas analíticas y generativas, fuentes y un comando único.

La muestra contiene 5.000 vectores sintéticos generados con semilla fija: shocks normales independientes, correlación parcial explícita y estado compartido de crisis con probabilidad fijada en 2.5%. Las cifras son unidades dimensionales ilustrativas. No son datos de SFC/BanRep, observaciones, una estimación de cartera o un pronóstico. Sin resultados contra mercado observado no se evalúan cobertura, forecast ni beneficio comercial.

**Madurez honesta:** TRL 2–3 (formulación y validación de concepto en entorno de laboratorio); no validado por modelo independiente, no conectado a datos, no aprobado para límites, capital, trading ni reporte regulatorio. Requiere gobierno de pesos, definición de instrumentos/factores, historia de shocks, horizonte, controles, reconciliación con revaluación, validación y no objeción cuando corresponda.

El comando `bash 04-quant-strategy-and-products/risk-engines/es-attribution-audit/run.sh` corre tests, análisis estático disponible, ejecuta cada celda de código del notebook en un proceso Python compartido y regenera outputs/figura. Python 3.12; matplotlib opcional solo para figura. El ejecutor no usa kernel Jupyter ni sockets y no declara validación de kernel. El método y estado están registrados en `results/notebook-execution.json`.
