# Laboratorio de notebooks de fraude y anomalías

Ocho experimentos especializados: dos por carpeta, 304 celdas en total, 88 celdas de código y 31 figuras guardadas. Todos usan datos sintéticos, semilla explícita, ecuaciones, comprobaciones y discusión de límites. Se conservan los resultados negativos y los contraejemplos.

| Carpeta | Notebook de fundamentos | Notebook de decisión y robustez |
|---|---|---|
| KYC | [Bayes, evidencia duplicada y calibración](../01-identity-kyc-consistency/notebooks/01-bayes-evidence-and-calibration.ipynb) | [Umbrales económicos y capacidad](../01-identity-kyc-consistency/notebooks/02-economic-thresholds-and-capacity.ipynb) |
| Redes | [Variables temporales y fuga](../02-temporal-application-graphs/notebooks/01-point-in-time-graph-features.ipynb) | [Cobertura y pérdida compartida](../02-temporal-application-graphs/notebooks/02-network-overlap-and-loss-coverage.ipynb) |
| Ingresos | [Cuantiles y cobertura](../03-income-document-consistency/notebooks/01-income-quantiles-and-coverage.ipynb) | [Conciliación y contaminación](../03-income-document-consistency/notebooks/02-flow-reconciliation-and-robustness.ipynb) |
| Proceso | [Mezcla y contracción de tasas](../04-origination-process-anomalies/notebooks/01-case-mix-and-shrinkage.ipynb) | [CUSUM, falsas alarmas y demora](../04-origination-process-anomalies/notebooks/02-cusum-false-alarms-and-delay.ipynb) |

## Reproducción

Desde esta carpeta:

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python execute_notebooks.py
```

El modo predeterminado usa nbclient y un kernel Jupyter independiente por notebook. Si el entorno bloquea conexiones locales, se puede ejecutar con IPython en procesos independientes:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python execute_notebooks.py --execution-mode ipython
```

Cada celda se ejecuta en orden, los errores interrumpen el proceso y las salidas MIME se guardan dentro del notebook. No se aceptan notebooks con errores ni resúmenes sin métricas computadas. `--qa-dir /ruta/temporal` exporta HTML y las figuras para inspección; esas previsualizaciones no son entradas del análisis.

`build_notebooks.py` reconstruye las celdas fuente con IDs estables y **borra las salidas de ejecución**. No es necesario ejecutarlo para reproducir: usarlo solo cuando se edite el scaffold y después volver a ejecutar los notebooks.

## Evidencia local

El entorno de esta entrega impidió abrir sockets de kernels, tanto TCP como IPC. La validación local utilizó `--execution-mode ipython`, un proceso separado por archivo, conservando tablas, figuras, comprobaciones y conteos de ejecución. [execution_evidence.json](execution_evidence.json) registra métricas, tiempos y SHA-256 de los ocho archivos guardados.

Se revisaron las 31 figuras: las 16 originales son idénticas byte a byte a las ya inspeccionadas, y se inspeccionaron las 15 nuevas. Los HTML de previsualización se exportaron; su estructura contiene el resumen, las secciones y las salidas esperadas. Las ecuaciones quedan en LaTeX para el renderizador de notebooks. La ejecución con nbclient queda cubierta por el workflow remoto, cuyo resultado debe consultarse para el commit correspondiente.

## Resultados para interpretar, no para extrapolar

- Duplicar una misma evidencia bajo falsa independencia mueve el posterior de 0,2081 a 0,7293.
- En el ejemplo de cobertura, investigar conjuntos solapados obtiene 110.000 COP de beneficio supuesto, frente a 220.000 con asignación conjunta y el mismo número de acciones.
- La banda de ingreso nominal 80% cubre 78,29% del test sintético; un desplazamiento de 0,4 log puntos reduce cobertura a 20,57%. No garantiza cobertura por segmento o bajo cambio de régimen.
- CUSUM se calibra con 600 trayectorias y se evalúa en otras 600: la falsa alarma a horizonte 120 días es 6,33%, con intervalo Wilson calculado en el notebook. No es tasa diaria ni control simultáneo de todos los canales.

Los experimentos son prototipos S2 acotados. La integración de los cuatro especialistas, los pipelines de datos reales y la estimación de fraude adjudicado siguen pendientes. Un conteo, una discrepancia de ingreso o un desvío de proceso no confirma fraude.

## Profundización de modelos y fórmulas

Cada notebook añade derivaciones, un diccionario de símbolos/unidades y una tabla de modelos/usos. Los nuevos ajustes incluyen logit individual/red, ingreso cero/monto positivo y beta-binomial. Se contrastan gradientes, límites de información y capacidad, supuestos de cobertura, conciliación e incertidumbre de proceso. Véanse el [catálogo](../MODEL_CATALOG.md) y la [revisión](../REVIEW_AND_RESULTS.md).
