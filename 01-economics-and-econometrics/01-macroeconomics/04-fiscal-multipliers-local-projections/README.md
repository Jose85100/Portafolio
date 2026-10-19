# Fiscal multipliers — local projections and identification

**Estado:** diseño econométrico avanzado + notebook sintético existente. No hay estimación causal sobre datos observados.

## 1. Pregunta y estimando
Sea `g_t` una innovación fiscal y `y_t` el logaritmo del producto real. Se busca la respuesta causal dinámica de `y` a una innovación de política fiscal exógena. Para cada horizonte `h=0,...,H`:
```math
y_{t+h}-y_{t-1}=\alpha_h+\beta_h g_t+\Gamma_h'X_{t-1}+u_{t+h}^{(h)}.
```
La interpretación de `beta_h` como respuesta causal exige que `g_t` sea ortogonal a innovaciones potenciales futuras, condicional en información predeterminada. Si `g_t` está medido en puntos de PIB y el lado izquierdo es log-PIB, `beta_h` **no es automáticamente** un multiplicador monetario. Para un multiplicador acumulado se requieren variaciones de producto y gasto en unidades comparables:
```math
M_H=\frac{\sum_{h=0}^{H}\Delta Y_{t+h}}{\sum_{h=0}^{H}\Delta G_{t+h}}.
```
No debe confundirse una razón de respuestas estimadas con la respuesta de una razón.

## 2. Derivación e identificación
Las proyecciones locales estiman por separado la proyección lineal a cada horizonte. Bajo exogeneidad condicional y especificación suficiente, el coeficiente del shock corresponde a la respuesta media parcial. El teorema de Frisch–Waugh–Lovell permite residualizar `g_t` e `y_{t+h}` respecto a `X_{t-1}`: `beta_h = Cov(g_t^perp,y_{t+h}^perp)/Var(g_t^perp)`. Si `Cov(g_t^perp,u_{t+h}) != 0`, aparece sesgo de endogeneidad. Una regla fiscal que reacciona al ciclo viola esa condición incluso con buen ajuste predictivo.

Con instrumento `z_t`, se necesita **relevancia** `Cov(z_t,g_t|X) != 0` y **exclusión** `Cov(z_t,u_{t+h}|X)=0`. El cociente IV residualizado identifica una respuesta local bajo supuestos adicionales, no un efecto universal de política.

## 3. Dependencia temporal e inferencia
Para `h>0`, las ventanas de resultado se solapan: los residuos pueden presentar correlación serial hasta orden aproximado `h`, aun cuando el shock sea innovacional. Errores estándar IID suelen subestimar incertidumbre. Utilizar HAC/Newey–West con sensibilidad de ancho de banda; comparar con bootstrap por bloques preservando la estructura temporal. En muestras cortas, revisar cobertura mediante simulaciones, no confiar únicamente en asintótica.

Las respuestas estimadas por horizonte pueden oscilar: LP reduce restricciones dinámicas frente a VAR, pero puede incrementar varianza. Reportar bandas **puntuales y simultáneas** cuando se inspeccionan muchos horizontes; no interpretar una banda puntual como control de error familiar.

## 4. Diseño de experimento reproducible
1. Simular un VAR estable con shock fiscal estructural conocido, persistencia del producto y retroalimentación fiscal.
2. Comparar LP OLS, LP-IV y VAR correctamente especificado, manteniendo idénticas innovaciones.
3. Introducir endogeneidad del shock, instrumento débil, cambio de régimen, error de medición y shocks correlacionados.
4. Medir sesgo `E[beta_hat]-beta`, RMSE, cobertura nominal, tasa de rechazo de falsaciones y tiempo de ejecución por horizonte.
5. Hacer placebo con anticipos del shock, comparar especificaciones de rezagos y reportar sensibilidad a transformaciones.

## 5. Protocolo empírico (pendiente)
Definir país, unidad temporal, deflactores, ajustes estacionales, revisiones/vintages, clasificación de gasto y tratamiento de episodios extraordinarios. Documentar fecha de descarga, licencia y código de construcción de series. Distinguir shocks narrativos, sorpresas presupuestales e instrumentos externos. No usar resultados sintéticos como evidencia del multiplicador de Colombia.

## 6. Interpretación financiera
El multiplicador depende del estado de capacidad ociosa, régimen monetario, restricciones de financiamiento, apertura y composición del gasto. Un aumento del PIB no implica necesariamente mejora de solvencia soberana: incluir respuesta de tasas, deuda/PIB, recaudo y primas de riesgo. Un stress test debe propagar **bandas de incertidumbre**, no solo el estimado central.

## 7. Preguntas de falsación
- ¿Qué variable no debería responder antes de la sorpresa fiscal?
- ¿La relevancia del instrumento sobrevive a cambios de muestra?
- ¿Qué parte del resultado depende de la unidad de medida?
- ¿Se mantienen las conclusiones con bandas simultáneas?
- ¿Qué mecanismo explica heterogeneidad entre recesión y expansión?

## 8. Bibliografía fundacional
- Jordà (2005), *Estimation and Inference of Impulse Responses by Local Projections*, AER.
- Ramey (2011), *Identifying Government Spending Shocks: It's All in the Timing*, QJE.
- Stock & Watson (2018), *Identification and Estimation of Dynamic Causal Effects in Macroeconomics Using External Instruments*, Economic Journal.
- Newey & West (1987), *A Simple, Positive Semi-definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix*, Econometrica.

[Notebook actual](notebooks/01-estimation-and-robustness.ipynb) — baseline sintético, no validación empírica. [Laboratorio de identificación](../../research-methods/).
