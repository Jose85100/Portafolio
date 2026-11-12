# Laboratorio de backtesting crediticio — versión ampliada

Seis notebooks Jupyter con **formulación matemática Markdown/LaTeX**, definiciones, supuestos, código Python, controles y visualizaciones condicionadas a datos reales.

## Orden de ejecución
1. `01_calidad_y_modelo_datos.ipynb`
2. `02_snapshots_y_cosechas.ipynb`
3. `03_planos_y_transiciones.ipynb`
4. `04_variables_territorio_y_transacciones.ipynb`
5. `05_eda_clusters_anomalias_modelos.ipynb`
6. `06_diccionario_y_sql_athena.ipynb`

### Datos
Los CSV `plantilla_*.csv` contienen encabezados y **no** observaciones. Los notebooks no generan resultados sintéticos ni afirman hallazgos. Las tablas adicionales de cliente, ciudad, TPV y buró son fuentes por identificar en AWS. La ejecución local con CSV vacíos valida estructura y flujos de ausencia de datos, no el comportamiento estadístico con datos productivos.

### Requisitos
`pip install notebook nbformat nbclient pandas numpy matplotlib scikit-learn`

### Advertencias metodológicas
- EVER y OVER requieren denominadores distintos, control de maduración y censura.
- MOB y corte calendario son ejes diferentes.
- Variables predictoras deben ser *point-in-time*; no usar transacciones futuras en modelos de originación.
- La versión actual implementa análisis exploratorio y especificaciones de modelos, **no** un motor de entrenamiento, tuning y validación de producción.
- Revisar SQL de origen: nombres de DPD, intervalos de vigencia, duplicación por joins, definición 30+ y tratamiento de castigos/migraciones.
