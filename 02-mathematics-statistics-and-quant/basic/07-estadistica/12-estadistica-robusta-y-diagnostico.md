# 12. Estadística robusta y diagnóstico de datos

**Objetivo:** entender la sensibilidad de los resúmenes antes de ajustar un modelo. Prerrequisito: estadística descriptiva. [Notebook de regresión y sensibilidad](notebooks/07-regresion-y-residuos.ipynb).

## Media y mediana ante un extremo

Para (1,2,3,4,5), ambas valen 3. Si el último dato cambia a 100, la media pasa a 22 y la mediana sigue en 3. La mediana resiste este cambio, pero no responde la misma pregunta que la media. Si importa el total monetario, ignorar un valor grande legítimo puede ocultar exposición real.

Una medida robusta de dispersión es la desviación absoluta mediana:
$$MAD=\operatorname{mediana}(|x_i-\operatorname{mediana}(x)|).$$
Para (1,2,3,4,100), las distancias son (2,1,0,1,97); MAD=1. Algunas aplicaciones multiplican por aproximadamente 1.4826 para consistencia bajo normalidad; no es una identidad válida para cualquier distribución.

## Faltantes y observaciones repetidas

Un faltante no equivale a cero. Si ingresos altos se omiten con más frecuencia, usar solo los observados puede sesgar la media. Imputar requiere hipótesis; registra cuántos datos faltan y qué mecanismo podría explicar la ausencia.

Una repetición tampoco siempre es un duplicado: dos transacciones iguales pueden ser legítimas. Para distinguirlas, define la unidad de observación y una clave antes de borrar filas.

## Diagnóstico no es condena

La regla de 1.5 veces el rango intercuartílico marca candidatos a inspección. No establece fraude ni error de captura. En distribuciones de cola pesada, valores alejados pueden ser parte del fenómeno. Compara análisis con y sin extremos, verifica unidades y examina su procedencia.

## Ejercicios con solución

1. Media y mediana de (1,2,3,4,100): 22 y 3.
2. MAD de esos datos: 1, sin factor de escala.
3. ¿Eliminar siempre el mayor 1% mejora un modelo? No. Cambia la población de análisis y puede eliminar eventos relevantes para riesgo.
4. ¿Datos sin faltantes son necesariamente buenos? No: pueden tener unidades mezcladas, selección sesgada o mediciones incorrectas.

**Regla de trabajo:** documenta correcciones y conserva trazabilidad; una limpieza silenciosa puede alterar el significado de los resultados.

