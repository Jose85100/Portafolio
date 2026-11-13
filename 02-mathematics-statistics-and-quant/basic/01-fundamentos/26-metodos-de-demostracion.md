# 26. Cómo construir y revisar una demostración

**Pregunta:** ¿qué hace que un argumento sea válido para todos los casos?  
**Objetivo:** practicar implicación, contraposición, contradicción e inducción. **Antes:** lección 8.

## 1. Separar hipótesis y conclusión

Una proposición del tipo P⇒Q dice que cuando P se cumple, Q también. No afirma que P sea cierto en todo contexto ni que Q implique P. Ejemplo: «si n es múltiplo de 6, entonces es múltiplo de 3». La recíproca falla para n=3.

Una demostración debe dejar claro de dónde parte. Escribir una cadena de ecuaciones verdadera no basta si no conecta hipótesis y conclusión.

## 2. Demostración directa

Proposición: el producto de dos enteros impares es impar.

Hipótesis: a=2m+1 y b=2n+1 para enteros m,n. Entonces:
$$ab=(2m+1)(2n+1)=4mn+2m+2n+1.$$
Agrupamos:
$$ab=2(2mn+m+n)+1.$$
El paréntesis es entero, así que la expresión tiene la forma de un impar. No hemos usado ejemplos particulares.

## 3. Contraposición

P⇒Q es equivalente a ¬Q⇒¬P. Demostraremos: si n² es par, n es par.

La contraposición dice: si n no es par, n² no es par. Como todo entero no par es impar, n=2k+1 y:
$$n^2=2(2k^2+2k)+1,$$
que es impar. Concluimos la implicación original.

No confundas contraposición con recíproca. En general, Q⇒P no es equivalente a P⇒Q.

## 4. Contradicción

Para demostrar que no existe un mayor entero, supón que M fuera ese mayor entero. M+1 es entero y supera M, contradicción. La hipótesis de existencia queda descartada.

La contradicción debe afectar a una afirmación establecida: una definición, un supuesto o un teorema válido. «No me parece posible» no es una contradicción matemática.

## 5. Inducción y su punto de inicio

Demostremos 2ⁿ≥n+1 para enteros n≥0.

**Base:** n=0 da 1≥1.  
**Paso:** suponiendo 2ⁿ≥n+1:
$$2^{n+1}=2\cdot2^n\ge2(n+1)\ge n+2,$$
porque n≥0 implica 2n+2≥n+2. Con base y paso probados, la afirmación vale para todo n≥0.

Omitir la base es un error: un paso lógico puede transmitir una propiedad sin que esta se cumpla en ningún punto inicial.

## 6. Revisar un argumento que parece correcto

Falsa prueba de que 1=2: toma a=b=1. De a²=ab, resta b²:
$$(a-b)(a+b)=b(a-b).$$
Cancelar a−b llevaría a a+b=b. Pero a−b=0: la cancelación divide por cero. La igualdad antes de cancelar era 0=0 y no aportaba esa información.

**Lista de revisión:** dominio de cada expresión; divisores no nulos; signos al multiplicar desigualdades; equivalencia o implicación de cada paso; tratamiento de fronteras.

## Ejercicios con solución

1. Refuta «si ab=0, entonces a=0 y b=0». Basta a=0,b=1; solo se concluye que al menos uno es cero.
2. Demuestra que la suma de tres enteros consecutivos es múltiplo de 3. n+(n+1)+(n+2)=3(n+1).
3. Prueba 1+3+…+(2n−1)=n². Base n=1. Paso: n²+(2n+1)=(n+1)².
4. ¿Diez mil pruebas numéricas demuestran una identidad universal? No; pueden detectar errores y aportar evidencia finita, pero no cubren todos los casos.

**Práctica:** escribe una solución en tres columnas: afirmación, justificación y condiciones. Si una justificación depende de lo que buscas demostrar, puede haber razonamiento circular.
