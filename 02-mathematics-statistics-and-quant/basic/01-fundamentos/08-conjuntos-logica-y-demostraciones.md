# 8. Conjuntos, lógica y demostraciones

**Objetivo:** leer hipótesis con precisión y distinguir ejemplos de argumentos generales. Prerrequisito: álgebra.

## Conjuntos y cuantificadores

Un conjunto reúne elementos: $A=\{1,2,3\}$. Si $B=\{3,4\}$, entonces $A\cap B=\{3\}$ y $A\cup B=\{1,2,3,4\}$. El complemento depende del universo: en $U=\{1,2,3,4,5\}$, $A^c=\{4,5\}$. Sin universo declarado, «todo lo que no está en A» puede ser ambiguo.

$\forall x$ significa «para todo x»; $\exists x$, «existe al menos un x». La negación de «todos los modelos son correctos» es «existe un modelo que no es correcto», no «ninguno es correcto». El orden importa: $\forall x\,\exists y:y>x$ es verdadero en los reales, pero $\exists y\,\forall x:y>x$ es falso.

## Implicación y equivalencia

Si un entero es divisible por 4, es par. La recíproca es falsa: 6 es par y no es divisible por 4. Un solo contraejemplo refuta una afirmación universal. En cambio, verificar diez casos no la demuestra.

Para probar que la suma de dos enteros pares es par, escribe $a=2m$, $b=2n$ para enteros m,n. Entonces $a+b=2(m+n)$, múltiplo de 2. Cada paso conserva los supuestos.

## Inducción

Para demostrar $\sum_{k=1}^n k=n(n+1)/2$:
1. Base n=1: ambos lados valen 1.
2. Supón verdadera la fórmula para n.
3. Añade n+1: $n(n+1)/2+(n+1)=(n+1)(n+2)/2$.
Esto prueba el siguiente caso y, junto con la base, todos los enteros positivos.

## Ejercicios con solución

1. Niega «para todo x>0, x²>1». Solución: existe x>0 con x²≤1; x=1/2 es testigo.
2. ¿x²=4 implica x=2? No: x=-2 refuta la afirmación.
3. Prueba que el cuadrado de un impar es impar. Si x=2k+1, x²=4k²+4k+1=2(2k²+2k)+1.

**Aplicación:** un test numérico controla casos; una demostración establece una propiedad bajo hipótesis explícitas. Ambos sirven, pero cumplen funciones distintas.

