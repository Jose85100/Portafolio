# Inflation Expectations & Phillips Curve

## Pregunta de investigación
Inflación, brecha de producto y expectativas. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
pi_t = beta E_t pi_(t+1) + kappa x_t + u_t
\]

## Estrategia econométrica
Estimar persistencia y pendiente con OLS; discutir endogeneidad. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
El notebook conserva el laboratorio sintético. La aplicación observada usa IPC total empalmado e ISE de DANE para describir la asociación entre inflación realizada y actividad, con hash, vintage y transformaciones registrados; no dispone de expectativas observadas ni de una brecha del producto.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Inflación y costo de fondeo fintech.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.

## Aplicación observada

El [reporte](reports/observed_application.md) y el runner [`observed_application.py`](observed_application.py) usan variación interanual del IPC y del ISE para evaluar una relación inflación–actividad de forma descriptiva. La variable de actividad es un proxy, no una brecha del producto; el resultado no es una curva de Phillips estructural ni causal.

El runner recibe las rutas a los dos XLSX oficiales, verifica tamaño y SHA-256 y genera series emparejadas, coeficientes HAC, figuras y manifiesto. No incluye copias de los datos crudos. Ver la sección de reproducción del reporte para los argumentos `--ipc-source` y `--ise-source`.
