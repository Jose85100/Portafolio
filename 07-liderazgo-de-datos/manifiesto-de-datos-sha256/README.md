# Manifiesto de datos con SHA-256

Construcción de un manifiesto con hash SHA-256, tamaño y número de filas por archivo, y verificación de integridad posterior. Detecta una alteración de un archivo, un archivo faltante y uno nuevo no registrado.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Manifiesto construido:
  macro.csv: f6f26102e85fd2d0... 5871 bytes, 100 filas
  precios.csv: 19ea8856ff574cee... 5893 bytes, 100 filas
  tasas.csv: b856210406e7eadb... 5878 bytes, 100 filas
Verificacion inicial: sin hallazgos
Verificacion tras cambios:
   FALTA: macro.csv
   ALTERADO: tasas.csv
   NO REGISTRADO: nuevo.csv
```
