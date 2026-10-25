# 16. Reglas de derivación: de dónde salen

**Objetivo:** deducir producto, cociente y cadena, y aplicarlos a elasticidades.  
**Prerrequisito:** definición de derivada. **Pregunta guía:** ¿por qué no basta con derivar cada factor por separado?

## 1. La regla del producto

Sean f y g derivables en x. Sumamos y restamos f(x+h)g(x):
$$
\begin{aligned}
f(x+h)g(x+h)-f(x)g(x)
&=f(x+h)[g(x+h)-g(x)]\\
&\quad+g(x)[f(x+h)-f(x)].
\end{aligned}
$$
Dividir por h y tomar el límite produce:
$$
(fg)'=fg'+gf',
$$
porque derivabilidad implica continuidad y f(x+h)→f(x).

**Ejemplo:** para f=x² y g=eˣ:
$$(x^2e^x)'=x^2e^x+2xe^x=e^x(x^2+2x).$$
Multiplicar solo las derivadas daría 2xeˣ y perdería un término entero.

## 2. La regla del cociente

Sea u=f/g, con g(x)≠0 en un entorno del punto. Como ug=f, la regla del producto da:
$$u'g+ug'=f'.$$
Sustituir u=f/g y despejar:
$$
u'=\frac{f'g-fg'}{g^2}.
$$
La condición g≠0 es parte del resultado. Para (x+1)/(x−1):
$$
u'=\frac{(x-1)-(x+1)}{(x-1)^2}
=-\frac{2}{(x-1)^2},\quad x\ne1.
$$
La función decrece en cada uno de los intervalos separados por la singularidad; no debemos ignorar esa discontinuidad al comparar puntos entre intervalos.

## 3. La cadena mediante aproximaciones locales

Si g es derivable en x:
$$g(x+h)=g(x)+g'(x)h+o(h).$$
La notación o(h) significa que el residuo dividido por h tiende a cero. Si f es derivable en g(x):
$$f(g(x)+k)=f(g(x))+f'(g(x))k+o(k).$$
Sustituir k=g(x+h)−g(x), que es O(h), permite identificar el coeficiente de h:
$$
(f\circ g)'(x)=f'(g(x))g'(x).
$$
Esto también cubre el caso g'(x)=0; una demostración que divide directamente por g(x+h)−g(x) necesita cuidar los puntos donde ese incremento es cero.

Para ln(1+x²):
$$
\frac{d}{dx}\ln(1+x^2)=\frac{1}{1+x^2}\cdot2x.
$$
El argumento del logaritmo es positivo para todo real x; no hay exclusiones adicionales.

## 4. Derivación implícita

En una curva dada por x²+y²=25, si y es una función derivable de x cerca del punto:
$$2x+2y\,y'=0\Rightarrow y'=-x/y,\quad y\ne0.$$
En (3,4), la pendiente es −3/4. En (5,0), la fórmula no sirve para y como función derivable de x: hay tangente vertical y el supuesto local falla.

## 5. Elasticidad como derivada logarítmica

Para Q(P)>0 y P>0:
$$
\frac{d\ln Q}{d\ln P}
=\frac{d\ln Q/dP}{d\ln P/dP}
=\frac{Q'/Q}{1/P}
=Q'\frac{P}{Q}.
$$
Si Q=AP^{-b}, con A,b>0:
$$Q'=-bAP^{-b-1}\Rightarrow Q'P/Q=-b.$$
Es una medida local adimensional. Para un cambio finito grande de precio, usar −b multiplicado por el porcentaje es una aproximación; la relación exacta es Q₂/Q₁=(P₂/P₁)^{-b}.

## Ejercicios con desarrollo

1. Deriva x·ln x, x>0. Producto: ln x+x/x=ln x+1.
2. Deriva e^(−x²). Cadena: −2xe^(−x²).
3. Para Q=100P^(−2), ¿subir P de 1 a 1.1 reduce Q exactamente 20%? No: Q₂/Q₁=1/1.1²≈0.82645; baja aproximadamente 17.36%.
4. Deriva 1/(1+x). Cociente o potencia y cadena: −1/(1+x)², x≠−1.

**Conexión:** estas reglas preparan para funciones de costo, log-verosimilitud y optimización; indicar el dominio sigue siendo indispensable.
