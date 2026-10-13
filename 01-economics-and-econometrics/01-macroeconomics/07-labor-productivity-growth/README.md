# Labor Productivity & Growth Accounting

## Pregunta de investigación
Crecimiento y productividad. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
Delta ln Y = alpha Delta ln K + (1-alpha) Delta ln L + Delta ln A
\]

## Estrategia econométrica
Descomposición y error de medición. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
Primera versión con datos sintéticos reproducibles. Futuras fuentes públicas posibles: Banco de la República, DANE, Superfinanciera, BIS, World Bank y FRED, según la variable y licencias. No se han descargado ni validado series reales. Guardar fecha de consulta, frecuencia, transformaciones, unidades y vintages.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Impacto de IA en productividad.
