# Reglas de calidad de datos

Marco de reglas de calidad de datos sobre una tabla de clientes con problemas inyectados: completitud, unicidad, rangos válidos, integridad referencial y actualidad. Produce un reporte con tasa de cumplimiento y filas fallidas por regla.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
cumplimiento  filas_fallidas  estado
completitud edad               0.961              39  ALERTA
unicidad cliente_id            0.996               4      OK
rango edad 18-100              0.985              15  ALERTA
ingreso positivo               0.975              25  ALERTA
ciudad existe                  0.970              30  ALERTA
actualizado <= 60 dias         0.940              60   FALLA
Indice global de calidad (promedio de reglas): 0.971
```
