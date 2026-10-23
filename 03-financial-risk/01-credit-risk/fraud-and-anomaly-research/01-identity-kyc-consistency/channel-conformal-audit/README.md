# Alertas KYC calibradas por canal

Auditoría incremental de rangos conformales para scores de anomalía fijos. Pregunta: ¿un umbral global concentra falsas alertas en el canal más ruidoso? El MVP compara pooled con calibración por canal sin cambiar score, splits ni alpha.

## Reproducir (Python 3.12)

```bash
bash run.sh
```

Instala versiones directas fijadas, ejecuta tests/cobertura/lint/tipos del núcleo, experimento y notebook. Se recomienda entorno virtual: `python -m venv .venv` y activarlo antes. Produce CSV/JSON, figura y notebook con outputs visibles. No requiere red después de instalar dependencias; no usa datos personales.

## Resultado sintético

60 semillas, 499 inliers de calibración por canal y 2.000 inliers de prueba por canal/semilla. Canal sigma=1/4. FPR pooled: 0%/9,754%; por canal: 4,630%/5,020%. Brecha disminuye 9,364 puntos porcentuales, superando el umbral ex ante de 3 pp. Una tasa observada 5,020% no contradice validez marginal <=5%: hay error Monte Carlo y calibración aleatoria. CSV incluye error estándar entre semillas.

Drift y sparse son resultados negativos intencionales: con dispersión de evaluación x1,7, FPR por canal 24,107%/24,846%; con nueve calibraciones por canal no se puede alertar al 5% (p mínimo=10%). Pooled también se abstiene en sparse (18 muestras, mínimo 1/19>5%).

Núcleo tipado sin dependencias externas: `src/conformal.py`. `ChannelCalibrator` rechaza canales desconocidos; no hay fallback silencioso. Score y particiones deben fijarse antes de calibrar. Alertar no prueba fraude y no autoriza rechazo automático.

Madurez: componente implementado y verificado con datos sintéticos; no se eleva la madurez del pilar ni se declara validación independiente empírica/operación. Revisión externa del ciclo pendiente. Ver `informe.md`, `MVP.md`, `referencias.bib` y `results/`.

Notebook ejecutado secuencialmente en proceso con IPython; el kernel ZeroMQ no arranca en este entorno por restricción de interfaces. Outputs proceden de ejecución real. El generador registra este modo en metadatos. Inspección de la figura separada del notebook; no se afirma render HTML completo.

## Ampliación del notebook — 23 de octubre

El notebook incorpora fórmulas, diccionario de variables en contexto, reconstrucción de cálculos, sensibilidad y casos negativos. `run.sh` conserva esta ampliación después de regenerar el estudio original. La extensión se mantiene en `scripts/deepen_20261023_notebooks.py` y `scripts/research_depth_experiments.py` desde la raíz; las celdas realmente se ejecutan y guardan sus salidas. [Revisión de alcance](../../../../../reviews/2026-10-23-alignment/README.md).
