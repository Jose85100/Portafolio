# Pérdida esperada por producto (PD, LGD, EAD)

Cálculo de la pérdida esperada EL = PD x LGD x EAD a nivel de crédito para cuatro productos, con distribuciones beta para PD y LGD, y verificación por simulación Monte Carlo de incumplimientos.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
exposicion             EL  EL/exposicion  perdida_simulada_media  participacion_EL
producto                                                                                            
consumo      32,661,624.8039 1,279,676.3118         0.0392          1,284,487.2521            0.3632
tarjeta      16,297,898.7389 1,119,808.0674         0.0687          1,121,181.4851            0.3178
vehiculo     57,704,772.6350   698,922.2269         0.0121            690,262.5757            0.1983
hipotecario 143,611,411.3453   425,355.7590         0.0030            422,339.8035            0.1207
EL total = 3,523,762 sobre exposicion 250,275,708
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
