# 20. Estimación y máxima verosimilitud

**Objetivo:** construir un estimador a partir de un modelo probabilístico y revisar sesgo y fronteras.  
**Prerrequisitos:** probabilidad, derivadas y estadística. **Pregunta guía:** ¿qué significa que un parámetro haga más plausibles los datos?

## 1. Dato observado frente a parámetro desconocido

Una vez observados los datos x₁,…,xₙ, los tratamos como fijos al estudiar la verosimilitud L(θ). Es la probabilidad de esos datos, o su densidad, vista como función del parámetro.

No es una distribución de probabilidad sobre θ. Para obtener una posterior bayesiana haría falta además una distribución previa y aplicar Bayes.

## 2. Bernoulli: derivación completa

Supón ensayos IID Xᵢ∈{0,1} con probabilidad p. Si k=Σxᵢ:
$$L(p)=\prod_{i=1}^np^{x_i}(1-p)^{1-x_i}=p^k(1-p)^{n-k}.$$
El logaritmo es creciente, así que maximizar L equivale a maximizar:
$$\ell(p)=k\ln p+(n-k)\ln(1-p),\quad0<p<1.$$
Derivamos:
$$\ell'(p)=\frac{k}{p}-\frac{n-k}{1-p}.$$
Igualar a cero y multiplicar por p(1−p)>0 produce:
$$k(1-p)-(n-k)p=0\Rightarrow k-np=0.$$
Por tanto:
$$\hat p=k/n.$$
Para 0<k<n:
$$\ell''(p)=-k/p^2-(n-k)/(1-p)^2<0,$$
lo que confirma máximo único interior.

Si k=0 o k=n, hay que revisar la frontera: en el espacio cerrado p∈[0,1], los máximos son 0 y 1, respectivamente. Si se restringe a (0,1), solo existe supremo, no máximo alcanzado. No dividas ni evalúes logaritmos en cero sin tratar estos casos.

## 3. Sesgo y varianza del estimador

Como p̂ es la media de Bernoulli:
$$E[\hat p]=\frac1n\sum_iE[X_i]=p.$$
Así es insesgado. Con independencia:
$$\operatorname{Var}(\hat p)=\frac{1}{n^2}\sum_i p(1-p)=\frac{p(1-p)}n.$$
Una muestra concreta puede producir p̂ lejos de p; insesgado significa correcto en promedio de repeticiones, no exacto en cada muestra.

Con n=100 y k=7, p̂=0.07. El error estándar estimado es √(0.07·0.93/100)≈0.0255. Es una aproximación de incertidumbre, no una garantía; con conteos pequeños y fronteras, un intervalo normal puede comportarse mal.

## 4. Normal: por qué aparece la media

Si Xᵢ son IID normales con media μ y varianza σ² conocida:
$$
\ell(\mu)=C-\frac1{2\sigma^2}\sum_i(x_i-\mu)^2.
$$
Derivar:
$$\ell'(\mu)=\frac1{\sigma^2}\sum_i(x_i-\mu)=0
\Rightarrow\hat\mu=\bar x.$$
La segunda derivada es −n/σ²<0. Bajo este modelo, máxima verosimilitud y mínimos cuadrados para la media coinciden.

Si σ² también es desconocida, su estimador de máxima verosimilitud es:
$$\hat\sigma^2_{\mathrm{ML}}=\frac1n\sum_i(x_i-\bar x)^2.$$
No coincide con el estimador insesgado de denominador n−1:
$$E[\hat\sigma^2_{\mathrm{ML}}]=\frac{n-1}{n}\sigma^2.$$

## Ejercicios con solución

1. Ocho éxitos en 40 observaciones: p̂=0.2.
2. Cero éxitos en 40: p̂=0 en [0,1], pero eso no demuestra que el verdadero p sea cero.
3. Datos (1,2,3): μ̂=2; varianza ML=(1+0+1)/3=2/3; insesgada=1.
4. ¿La independencia importa? Sí: permite factorizar la verosimilitud y sumar varianzas sin covarianzas. Con dependencia, hay que formular otro modelo.

**Límite:** un máximo bien calculado puede pertenecer a un modelo mal especificado. Revisa diseño muestral, dependencia y compatibilidad de la distribución con los datos.
