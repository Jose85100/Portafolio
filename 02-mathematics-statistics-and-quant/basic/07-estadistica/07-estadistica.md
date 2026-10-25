# 7. Estadística: describir, estimar y reconocer límites

**Objetivo:** separar población y muestra, dispersión e incertidumbre, asociación y causalidad.

## Resumir sin ocultar

Para $x=(1,2,3,4,10)$, la media es $\bar x=20/5=4$; la mediana es 3. El valor 10 desplaza la media. Ningún resumen sustituye revisar distribución, unidades, datos faltantes y origen de la muestra.

Las desviaciones respecto a 4 son $(-3,-2,-1,0,6)$; sus cuadrados suman 50. La varianza descriptiva de estos cinco valores como población es $50/5=10$. Como estimador insesgado de la varianza de una población de la que son una muestra IID con segundo momento finito, usamos
$$s^2=\frac{\sum_i(x_i-\bar x)^2}{n-1}=12.5.$$
Se pierde un grado de libertad al estimar la media: las desviaciones suman cero. La desviación estándar vuelve a las unidades originales.

## Incertidumbre sobre una media

La desviación estándar describe dispersión de observaciones; el error estándar de la media mide incertidumbre de la estimación. Bajo observaciones IID de varianza finita se estima con $s/\sqrt n$.

Para $n=25$, $\bar x=10$ y $s=2$, el error estándar es 0.4. Con población normal y varianza desconocida, un intervalo bilateral del 95% usa $t_{24,0.975}\approx2.064$:
$$10\pm2.064(0.4)=[9.1744,10.8256].$$
El procedimiento cubre la media fija en 95% de repeticiones bajo esos supuestos. No significa que 95% de observaciones esté en el intervalo ni asigna probabilidad frecuentista posterior al parámetro. Con muestras grandes puede emplearse una aproximación normal si sus condiciones se sostienen. En series temporales, autocorrelación puede invalidar el error estándar IID.

## Contrastes y regresión

Un valor p es, bajo la hipótesis nula y el modelo, la probabilidad de un estadístico tan extremo o más que el observado. No es la probabilidad de que la hipótesis nula sea verdadera. Reporta también tamaño del efecto, incertidumbre y diseño muestral.

En regresión simple con intercepto y $S_{xx}>0$:
$$\hat\beta_1=\frac{\sum(x_i-\bar x)(y_i-\bar y)}{\sum(x_i-\bar x)^2},\quad
\hat\beta_0=\bar y-\hat\beta_1\bar x.$$
Para $x=(1,2,3)$, $y=(2,3,5)$, medias 2 y $10/3$, numerador 3 y denominador 2: pendiente 1.5, intercepto $1/3$. Es un ajuste descriptivo; causalidad requiere supuestos adicionales sobre asignación y factores de confusión.

## Ejercicios y soluciones

1. Si sumas 7 a todos los datos, media y mediana aumentan 7; varianza no cambia.
2. Si duplicas todos los datos, media se duplica y varianza se multiplica por 4.
3. Cuadruplicar $n$, manteniendo $s$, reduce el error estándar a la mitad.
4. ¿Una muestra enorme elimina sesgo de selección? No: puede estimar con mucha precisión una cantidad distinta de la que interesa.

**Antes de modelar:** define población objetivo, unidad de observación, mecanismo de selección y momento de medición. Para predicción temporal separa entrenamiento y evaluación por tiempo; evita usar información futura.
