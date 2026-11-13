# Validación descriptiva con tarjetas UCI

[Notebook ejecutado](notebook.ipynb): compara Gini, KS, Brier, calibración y PSI de un modelo logístico en entrenamiento y prueba aleatoria del mismo periodo. Ajusta un modelo numérico propio: **no es la validación del scorecard WoE** del proyecto relacionado.

La fuente, su licencia, corte y SHA-256 están documentados en el [companion de scoring](../../../01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/README.md). Los umbrales de score y la estandarización se fijan en entrenamiento. El PSI entre particiones aleatorias es una comprobación de muestra, no drift temporal; no hay fechas individuales para un análisis fuera de tiempo. El ejercicio no determina aceptación regulatoria ni sustituye una validación independiente.

Desde la raíz del repositorio, con `requirements-research.txt` instalado:

```bash
python scripts/execute_notebooks.py --output artifacts/uci350 03-financial-risk/02-market-and-model-risk/validacion-de-modelo-psi-gini/observed-uci350/notebook.ipynb
```

En esta ejecución, el modelo numérico obtuvo en prueba AUC 0,7067, Gini 0,4133 y Brier 0,1470; el PSI entre particiones aleatorias fue 0,000605. La calibración agregada no elimina diferencias por banda: en la banda superior la probabilidad media fue 0,5749 frente a 0,6838 de frecuencia observada (759 clientes). No se propone una causa ni una recalibración sin evaluación adicional.
