# Detección de drift de datos con PSI y KS

Monitoreo de cambios de distribución entre un período de referencia y uno actual: PSI y prueba de Kolmogorov-Smirnov por variable, con niveles de alerta y un resumen de variables a revisar.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scipy
python3 main.py
```

## Resultado de ejemplo

```text
PSI      KS  p_valor_KS alerta
variable                                      
ingreso      0.1004  0.1325      0.0000  AMBAR
edad         0.0015  0.0118      0.4894  VERDE
utilizacion  0.3672  0.2366      0.0000   ROJO
antiguedad   0.0023  0.0260      0.0023  VERDE
Variables a revisar: ['ingreso', 'utilizacion']
```
