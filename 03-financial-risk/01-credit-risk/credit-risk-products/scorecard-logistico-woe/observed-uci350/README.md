# Scorecard WoE: benchmark observado UCI

Este companion utiliza el conjunto **Default of Credit Card Clients**, con 30.000 registros históricos de tarjetas de Taiwán y una etiqueta de impago del mes siguiente. El caso evalúa un scorecard sobre una partición aleatoria de clientes del mismo periodo; no es una evaluación fuera de tiempo, un score de originación ni evidencia de desempeño en Colombia.

- **Fuente:** I-Cheng Yeh (2009), [UCI Machine Learning Repository](https://doi.org/10.24432/C55S3H). Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); atribución al autor y repositorio.
- **Descarga oficial:** `https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip`; consultada el 12 de noviembre de 2026. Archivo XLS incluido sin modificar.
- **SHA-256 XLS:** `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`; el notebook verifica la huella, 30.000 filas, identificadores únicos y etiqueta binaria.
- **Grano:** cliente en el conjunto publicado; periodo de historia de pagos de abril a septiembre de 2005, con etiqueta de impago del mes siguiente. No contiene fechas individuales suficientes para un backtest de originación.
- **Variables:** cupo y estados históricos de pago; se excluyen identificador, edad, sexo, educación y estado civil del modelo. Los estados previos no se presumen disponibles en originación.
- **Método:** estratificación 75/25 por cliente con semilla 42. Cortes de cuantiles y WoE con suavizado 0,5 aprendidos en entrenamiento, regresión logística y AUC, Gini, KS, Brier y calibración en prueba. El WoE supervisado se aprende en el entrenamiento, por lo que métricas dentro de esa misma muestra serían optimistas.

## Reproducción

Desde la raíz del repositorio, instalar `requirements-research.txt` (incluye `xlrd`) y ejecutar:

```bash
python scripts/execute_notebooks.py --output artifacts/uci350 03-financial-risk/01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/notebook.ipynb
```

[Notebook ejecutado](notebook.ipynb). En la ejecución inicial, la muestra retenida de 7.500 registros dio AUC 0,7432 y Brier 0,1399. Las métricas reflejan esta partición y no constituyen un criterio institucional de aceptación. La etiqueta no es EVER >30 a MOB 3 y la evaluación no corrige sesgo de aprobación, cambios de política ni estabilidad temporal.
