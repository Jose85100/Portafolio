# Cap table y dilución por rondas

Simulación de cap table a lo largo de pre-semilla, semilla, serie A y serie B con aumento del pool de opciones pre-dinero. Calcula la propiedad de fundadores e inversionistas tras cada ronda y el valor de la participación de los fundadores.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install pandas
python3 main.py
```

## Resultado de ejemplo

```text
post_dinero_M  pool  fundadores  inv_semilla  valor_fundadores_M  inv_serie A  inv_serie B
ronda                                                                                              
semilla          7.500 0.100       0.700        0.200               5.250        0.000        0.000
serie A         40.000 0.120       0.529        0.151              21.156        0.200        0.000
serie B        140.000 0.100       0.434        0.124              60.702        0.164        0.179
Suma de participaciones tras la ultima ronda: 1.000
Fundadores: de 100% a 43.4%
```
