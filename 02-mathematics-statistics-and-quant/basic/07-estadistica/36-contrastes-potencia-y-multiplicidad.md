# 36. Contrastes: errores, potencia y comparaciones múltiples

**Pregunta:** ¿cómo decidir con incertidumbre sin confundir falta de evidencia con ausencia de efecto?  
**Objetivo:** construir un contraste sencillo y derivar su potencia. **Antes:** muestreo, normal y estadística básica.

## 1. Hipótesis y regla de decisión

Supón Xᵢ IID normales con media μ y desviación conocida σ. Queremos contrastar H₀:μ=μ₀ frente a H₁:μ≠μ₀. Bajo H₀:
$$Z=\frac{\bar X-\mu_0}{\sigma/\sqrt n}\sim N(0,1).$$
Un contraste bilateral de nivel α rechaza si |Z|>z_(1−α/2), donde zₚ es cuantil normal. Para α=0.05, el umbral es aproximadamente 1.96.

La regla se define antes de observar el resultado. Si escogemos después el contraste que más favorece la conclusión, el nivel nominal deja de describir el procedimiento realmente usado.

## 2. Errores de tipo I y II

Tipo I: rechazar H₀ cuando es verdadera. El nivel α controla su probabilidad bajo el modelo.

Tipo II: no rechazar H₀ cuando una alternativa específica es verdadera. Su probabilidad es β(μ); la potencia es 1−β(μ).

No rechazar no equivale a demostrar igualdad: una muestra pequeña puede tener poca potencia frente a diferencias importantes.

## 3. Derivar la potencia

Si la verdadera media es μ₁, el estadístico Z tiene distribución normal de varianza uno y media:
$$\delta=\frac{(\mu_1-\mu_0)\sqrt n}{\sigma}.$$
Con c=z_(1−α/2):
$$
\operatorname{Potencia}(\mu_1)=P(Z>c)+P(Z<-c)
=1-\Phi(c-\delta)+\Phi(-c-\delta).
$$
La potencia aumenta al crecer el efecto estandarizado o el tamaño muestral. No es una propiedad fija del test sin especificar una alternativa.

Para n=100,σ=10 y μ₁−μ₀=2, δ=2. Con c≈1.96, la potencia es aproximadamente 0.516, no 95%. Un nivel de 5% no implica un 95% de probabilidad de detectar cualquier efecto.

## 4. Valor p y tamaño del efecto

En este contraste, p=2[1−Φ(|z_obs|)]. Describe cuán extremo es el estadístico bajo H₀; no es P(H₀|datos).

Ejemplo: diferencia observada 2, σ=10,n=100 da z=2 y p≈0.0455. Con el mismo efecto observado y n=25, z=1 y p≈0.3173. El efecto es idéntico; cambia la precisión.

Reporta diferencia en unidades originales e intervalo, no solo el valor p. En el modelo conocido, un intervalo 95% es x̄±1.96σ/√n. Rechazar H₀ equivale a que μ₀ quede fuera de ese intervalo bilateral con el mismo nivel.

## 5. Comparaciones múltiples

Si hacemos m contrastes independientes, todos con nulas verdaderas y nivel α:
$$P(\text{al menos un falso rechazo})=1-(1-\alpha)^m.$$
Con m=20 y α=0.05, vale aproximadamente 0.6415.

Bonferroni usa nivel α/m por contraste. Por la cota de la unión:
$$P\left(\bigcup_{j=1}^m\{\text{falso rechazo}_j\}\right)
\le\sum_{j=1}^m\frac{\alpha}{m}=\alpha.$$
La garantía no requiere independencia, pero puede ser conservadora. Controlar falsos descubrimientos es otro objetivo y necesita otro procedimiento explícito.

## Ejercicios y soluciones

1. ¿p=0.03 significa 97% de probabilidad de H₁? No.
2. Con m=10 y α global 0.05, Bonferroni usa 0.005 por contraste.
3. ¿Un resultado significativo demuestra relevancia práctica? No: depende del tamaño del efecto, costos y contexto.
4. Si σ es desconocida con datos IID normales, se usa un estadístico t con s y n−1 grados de libertad; no se intercambian sin justificar los cuantiles.

**Límite:** selección, dependencia y especificación errónea pueden invalidar el control de error, aunque la fórmula se calcule correctamente.
