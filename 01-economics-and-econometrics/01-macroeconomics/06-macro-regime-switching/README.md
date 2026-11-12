# Macro Regime Switching

## Pregunta de investigación
Recesión y expansión. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
P(s_t=j|s_(t-1)=i)=P_ij
\]

## Estrategia econométrica
Estimación de transiciones y validación de persistencia. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
El laboratorio original usa datos sintéticos reproducibles; el companion observado añade la serie mensual oficial del ISE de DANE y documenta vintage, fuente, grano, hash y regla del proxy. El companion clasifica el signo de la variación anual del ISE y resume transiciones empíricas; no estima un modelo Markov-switching ni identifica causas de los cambios.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Políticas de originación anticíclicas.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.

## Aplicación observada: signo del crecimiento del ISE

El [companion observado](reports/observed_application.md) usa la variación anual del ISE de DANE para construir dos estados observados: crecimiento interanual negativo y no negativo. Calcula transiciones mensuales y persistencia; es un proxy de régimen, no un modelo Markov-switching estimado ni una fecha oficial de recesión.

El crudo se lee desde la ruta canónica del Atlas, no está copiado en este producto. Reproducción:

```bash
python3 -m pip install openpyxl numpy matplotlib
python3 observed_application.py --ise-source "/ruta/a/Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/dane_ise_jul2026.xlsx"
```

El runner verifica hash y esquema antes de crear la serie derivada, la matriz de transición, la figura y el manifiesto de linaje. Los meses preliminares/provisionales se preservan como tales. La inferencia es descriptiva: no identifica causas de los cambios ni respuestas a política monetaria.
