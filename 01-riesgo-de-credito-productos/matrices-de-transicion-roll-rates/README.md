# Matrices de transición y roll rates

Estimación por máxima verosimilitud de una matriz de transición entre estados de mora (al día, 30, 60, 90+ días y default absorbente) a partir de historias simuladas, y cálculo de la PD acumulada a 12 meses con potencias de la matriz.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Matriz estimada (filas = estado actual):
         al_dia  mora_30  mora_60  mora_90  default
al_dia    0.940    0.050    0.000    0.000    0.010
mora_30   0.349    0.397    0.255    0.000    0.000
mora_60   0.145    0.104    0.350    0.402    0.000
mora_90   0.047    0.000    0.098    0.457    0.399
default   0.000    0.000    0.000    0.000    1.000
Error absoluto maximo vs matriz verdadera: 0.0068
PD acumulada a 12 meses (cuenta al dia): estimada 0.1653 | verdadera 0.1636
```
