# Spatial Econometrics

## Pregunta de investigación
Dependencia territorial. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
y=rho W y+X beta+eps
\]

## Estrategia econométrica
Autocorrelación espacial y reflexión. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
El laboratorio usa datos sintéticos reproducibles. La aplicación descriptiva complementaria utiliza valor agregado municipal observado del DANE y registra fuente, vintage, huella y transformaciones; su alcance y límites se detallan más abajo.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Riesgo regional.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.

## Aplicación observada: concentración territorial del valor agregado

El companion [observado](reports/observed_application.md) usa el valor agregado municipal del DANE, base 2015, para describir la concentración entre 1.123 códigos DIVIPOLA (2011–2023; 2024p se muestra aparte). El vintage incorpora Nuevo Belén de Bajirá con ceros anteriores a su creación, de acuerdo con la nota del cuadro. El runner [`observed_application.py`](observed_application.py) consume el XLSX canónico desde una ruta provista por el usuario y verifica su SHA-256, códigos DIVIPOLA, grano y completitud antes de generar métricas y figura. El raw no se duplica en este producto.

```bash
python3 observed_application.py --source "/ruta/a/Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/dane_valor_agregado_municipal_2011_2024p.xlsx"
```

Requiere `openpyxl`, `numpy` y `matplotlib`. La ruta completa de origen no queda registrada en los resultados.

La aplicación observada es una lectura distributiva de insumo territorial, no estima autocorrelación espacial, convergencia causal ni el parámetro `ρ` del modelo de rezago espacial. El laboratorio sintético sigue siendo el espacio para estudiar identificación y estimadores espaciales bajo mecanismos controlados; el companion establece qué patrón territorial debe explicar un análisis posterior y qué datos aún faltan para estimarlo.
