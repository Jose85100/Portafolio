# Tarjeta de crédito: backtesting de onboarding y mora temprana

Una política de originación necesita saber qué ocurrió durante los primeros meses de cada cosecha y si el comportamiento cambia por segmento. Este laboratorio organiza el cálculo de **EVER >30 a MOB 3**, en número y saldo, y presenta un recorrido para analizar originación, score, ubicación y avances de efectivo.

![Flujo de backtesting de onboarding](docs/flujo-onboarding.svg)

> **Estado:** plantillas y demostraciones didácticas; no hay cartera real ni validación institucional incluida. Los valores simulados se identifican en los notebooks y no representan desempeño de clientes. La política, las fuentes y las reglas deben validarse antes de una ejecución real.

## Recorrido

| Paso | Notebook | Pregunta |
|---|---|---|
| 1 | [Calidad y modelo de datos](01_calidad_y_modelo_datos.ipynb) | ¿Hay llaves, cortes y saldos suficientes para calcular? |
| 2 | [Snapshots y cosechas](02_snapshots_y_cosechas.ipynb) | ¿Cuál es el EVER >30 por número y saldo en cada MOB y cohorte? |
| 3 | [Planos y transiciones](03_planos_y_transiciones.ipynb) | ¿Cómo migran las cuentas entre estados de mora? |
| 4 | [Segmentos y avances](04_variables_territorio_y_transacciones.ipynb) | ¿Quién hizo avances, en qué momento y qué información estaba disponible? |
| 5 | [EDA, perfiles, anomalías y modelos](05_eda_clusters_anomalias_modelos.ipynb) | ¿Qué relaciones y perfiles merecen investigación sin fuga temporal? |
| 6 | [Diccionario y SQL Athena](06_diccionario_y_sql_athena.ipynb) | ¿Qué contratos y consultas se requieren para una extracción revisable? |

Los gráficos generados a partir de datos didácticos llevan una identificación explícita. Para usar un extracto propio, revisar el modo y los parámetros de cada notebook, mantener los datos sensibles fuera de Git y adaptar el contrato de entrada. Las consultas Athena son propuestas: **no se ejecutaron contra una fuente institucional**.

## Contrato inicial de la métrica

Por defecto, una cuenta tiene evento si presenta **DPD > 30** en alguno de los cortes MOB 1, 2 o 3. Una cuenta es evaluable si sus tres cortes y DPD están presentes. El número y el saldo tienen denominadores independientes; el saldo de ejemplo es el capital observado en MOB 3 y no representa pérdida. El motor también resume por cliente con las cuentas que aparecen en el panel.

Las convenciones se deben acordar con el dueño del indicador: `>30` frente a `≥30`, origen de MOB, unidad cuenta/cliente, saldo, cancelaciones y castigos. Conciliar el panel contra originación: las cuentas ausentes por completo del panel no aparecen en el universo calculado. Los cortes mensuales pueden omitir episodios intrames.

La [guía metodológica](GUIA_METODOLOGICA.md) explica fórmulas, segmentos, disponibilidad temporal, controles y limitaciones. Los [contratos de métricas](contratos_metricas.csv), [diccionario](diccionario_variables.csv) y `plantilla_*.csv` describen el intercambio esperado; las plantillas de datos contienen encabezados, no información real.

## Ejecutar

Desde la raíz del repositorio, en un entorno Python con los paquetes de `requirements-research.txt` instalados:

```bash
python -m pip install -r requirements-research.txt
python -m jupyter nbconvert --to notebook --execute --inplace 03-financial-risk/01-credit-risk/credit-vintage-snapshot-lab/02_snapshots_y_cosechas.ipynb
python -m unittest discover -s 03-financial-risk/01-credit-risk/credit-vintage-snapshot-lab/tests -v
```

Los notebooks 01 y 02 muestran por defecto una demostración ficticia; 03, 04 y 05 distinguen sus gráficos simulados de la ejecución con plantillas vacías. Para datos propios, siga las instrucciones de cada notebook y seleccione el archivo y modo adecuados. El notebook 05 incluye un AFM opcional que requiere `prince==0.20.2`; Kaplan–Meier, Cox y K-Prototypes están especificados como líneas futuras. La [plantilla de seguimiento en MOB 1](plantilla_modelado_mob1.csv) contiene solo encabezados y define un resultado posterior, no un score de originación. La instalación de Jupyter/`nbconvert` puede requerir `python -m pip install nbconvert` si el entorno no lo incluye.

## Análisis y gobierno

AFM mixto, perfiles, pruebas de asociación, supervivencia, modelos y anomalías se interpretan según el momento de decisión. Los avances posteriores no son predictores disponibles al originar; los perfiles deben ajustarse en entrenamiento y compararse fuera de tiempo. Anomalía, asociación o SHAP no prueban fraude ni causalidad. Revisar pequeñas muestras, sesgo de selección, estabilidad, calibración, privacidad y uso justo antes de tomar decisiones.
