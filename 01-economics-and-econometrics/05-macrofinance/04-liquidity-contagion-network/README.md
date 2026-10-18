# Liquidity Contagion Network

## Pregunta de investigación
Contagio de liquidez. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
L_i=max(0,outflows_i-inflows_i-buffer_i)
\]

## Estrategia econométrica
Simulación de cascadas. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
Primera versión con datos sintéticos reproducibles. Futuras fuentes públicas posibles: Banco de la República, DANE, Superfinanciera, BIS, World Bank y FRED, según la variable y licencias. No se han descargado ni validado series reales. Guardar fecha de consulta, frecuencia, transformaciones, unidades y vintages.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Pagos y tesorería.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.
