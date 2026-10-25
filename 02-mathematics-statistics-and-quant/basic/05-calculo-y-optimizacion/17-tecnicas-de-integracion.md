# 17. Integración: sustitución y partes, con derivaciones

**Objetivo:** reconocer estructura en una integral y escoger una transformación justificable.  
**Prerrequisitos:** integración básica y reglas de derivación. **Pregunta guía:** ¿cómo invertir una regla de derivación?

## 1. Sustitución: invertir la cadena

Si F'=f y g es derivable, entonces:
$$\frac{d}{dx}F(g(x))=f(g(x))g'(x).$$
Integrar ambos lados da:
$$\int f(g(x))g'(x)\,dx=F(g(x))+C.$$
Escribimos u=g(x), du=g'(x)dx como una forma de llevar la cuenta de esta identidad.

**Ejemplo:** ∫2x cos(x²)dx. Elegimos u=x² porque su derivada 2x aparece multiplicando. Así:
$$\int2x\cos(x^2)dx=\int\cos u\,du=\sin u+C=\sin(x^2)+C.$$
Verificar derivando la respuesta evita errores de factores.

## 2. Cambiar límites de manera consistente

Para:
$$\int_0^1 2xe^{x^2}dx,$$
u=x² lleva 0→0 y 1→1. Entonces:
$$\int_0^1 e^u du=e-1.$$
No mezcles límites en x con una integranda en u. Puedes transformar límites, o volver a x antes de evaluar, pero debes ser consistente.

En:
$$\int_0^2\frac{x}{1+x^2}dx,$$
u=1+x² y du=2x dx dan:
$$\frac12\int_1^5u^{-1}du=\frac12\ln5.$$
El factor 1/2 compensa que du contiene 2x y la integranda solo contiene x.

## 3. Integración por partes: invertir el producto

De (uv)'=u'v+uv' se obtiene:
$$\int uv'\,dx=uv-\int u'v\,dx.$$
En notación diferencial:
$$\int u\,dv=uv-\int v\,du.$$
Conviene elegir u de modo que derivarla simplifique el problema, aunque no existe una elección universal que siempre funcione.

**Ejemplo:** ∫xeˣdx. Toma u=x, du=dx, dv=eˣdx, v=eˣ:
$$\int xe^xdx=xe^x-\int e^xdx=(x-1)e^x+C.$$
Derivando: eˣ+(x−1)eˣ=xeˣ.

Para ∫ln x dx, x>0, escribe ln x·1. Con u=ln x y dv=dx:
$$\int\ln x\,dx=x\ln x-\int1\,dx=x\ln x-x+C.$$

## 4. Integrales impropias: primero el límite

La expresión ∫₁^∞x^(−p)dx significa:
$$\lim_{M\to\infty}\int_1^M x^{-p}dx.$$
Si p≠1:
$$\int_1^M x^{-p}dx=\frac{M^{1-p}-1}{1-p}.$$
Para p>1, M^(1−p)→0 y el valor es 1/(p−1). Para p<1 diverge. Si p=1, la integral es ln M y también diverge. Que la función tienda a cero no garantiza área finita.

## 5. Conexión con colas y momentos

Una densidad proporcional a x^(−α−1), x≥1, se normaliza con constante α>0. Su media requiere integrar αx^(−α), lo que converge solo si α>1. Tener una distribución válida no garantiza una media finita; menos aún una varianza finita.

## Ejercicios y soluciones

1. ∫3x²/(1+x³)dx: u=1+x³; resultado ln|1+x³|+C en intervalos que no cruzan −1.
2. ∫₀¹xeˣdx: evaluar (x−1)eˣ entre 0 y 1 da 1.
3. ∫₁^∞x^(−2)dx=1, mientras ∫₁^∞x^(−1)dx diverge.
4. ¿Es ∫₂^∞x^(−2)dx igual a 1? No: [−1/x]₂^∞=1/2; cambiar el límite inferior cambia el área.

**Error frecuente:** usar una antiderivada a través de una singularidad sin comprobar convergencia de los límites laterales.
