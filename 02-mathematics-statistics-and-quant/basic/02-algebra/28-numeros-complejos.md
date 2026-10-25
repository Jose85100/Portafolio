# 28. Números complejos: álgebra y rotaciones

**Pregunta:** ¿cómo resolver x²+1=0 y qué tiene que ver con girar un vector?  
**Objetivo:** operar con complejos y conectar forma cartesiana, polar y oscilaciones. **Antes:** álgebra y trigonometría.

## 1. Ampliar los números

Definimos i²=−1. Un complejo tiene forma z=a+bi, con a,b reales. Se identifica con el punto (a,b) del plano. La suma:
$$(a+bi)+(c+di)=(a+c)+(b+d)i$$
es suma por coordenadas. El producto se obtiene distribuyendo y usando i²=−1:
$$(a+bi)(c+di)=(ac-bd)+(ad+bc)i.$$

Ejemplo: (1+2i)(3−i)=3−i+6i−2i²=5+5i. No se trata de multiplicar coordenadas por separado.

## 2. Conjugado, módulo y división

El conjugado es z̄=a−bi. Entonces:
$$z\bar z=a^2+b^2=|z|^2,\quad |z|=\sqrt{a^2+b^2}.$$
Para z≠0:
$$\frac1z=\frac{\bar z}{|z|^2}.$$
Así:
$$\frac{1+2i}{3-i}=\frac{(1+2i)(3+i)}{10}=\frac{1+7i}{10}.$$
El módulo mide longitud; el conjugado refleja respecto al eje real.

## 3. Forma polar y multiplicación

Si z≠0, puede escribirse:
$$z=r(\cos\theta+i\sin\theta),\quad r=|z|.$$
El argumento θ se define salvo múltiplos de 2π. No uses arctan(b/a) sin revisar el cuadrante; una función atan2 considera ambos signos.

Las identidades de suma de ángulos muestran que multiplicar dos complejos multiplica sus módulos y suma sus argumentos. En particular, multiplicar por i gira 90°:
$$i(a+bi)=-b+ai.$$
El vector (a,b) pasa a (−b,a), conservando longitud.

## 4. Potencias y raíces

Por repetición del producto:
$$[\cos\theta+i\sin\theta]^n=\cos(n\theta)+i\sin(n\theta)$$
para enteros n≥0; es la fórmula de De Moivre. Usando la notación exponencial e^(iθ)=cosθ+i sinθ, que puede justificarse mediante series, se escribe z=re^(iθ).

Resolver wⁿ=z, para z≠0 y n entero positivo, da:
$$w_k=r^{1/n}\exp\left(i\frac{\theta+2\pi k}{n}\right),\quad k=0,\ldots,n-1.$$
Son n raíces distintas distribuidas uniformemente en un círculo. El valor z=0 se trata aparte: su única raíz es 0.

Para w²=−1, r=1 y θ=π: w=i o −i. Para w³=1, las raíces son 1 y −1/2±i√3/2.

## 5. Un vínculo con ecuaciones reales

La ecuación x²−2x+5=0 da:
$$x=\frac{2\pm\sqrt{-16}}2=1\pm2i.$$
Los complejos no reales aparecen por parejas conjugadas cuando el polinomio tiene coeficientes reales: conjugar P(z)=0 produce P(z̄)=0.

## Ejercicios y soluciones

1. (2+i)+(1−3i)=3−2i.
2. |3−4i|=5 y su inverso es (3+4i)/25.
3. (1+i)²=2i; (1+i)⁴=−4.
4. ¿Multiplicar por 2i conserva longitudes? No: gira 90° y multiplica la longitud por 2.

**Aplicación y límite:** complejos facilitan oscilaciones y autovalores de sistemas. No existe un orden de campo compatible con sus operaciones que extienda el orden usual de los reales; expresiones como z>0 no tienen el mismo significado general.
