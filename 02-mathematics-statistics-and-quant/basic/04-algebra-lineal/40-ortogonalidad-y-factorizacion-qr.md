# 40. Ortogonalidad y QR: resolver sin formar una inversa

**Pregunta:** ¿cómo construir ejes ortogonales para calcular proyecciones y regresiones?  
**Objetivo:** derivar Gram–Schmidt y resolver mínimos cuadrados mediante QR. **Antes:** bases, producto interno y mínimos cuadrados.

## 1. Proyección sobre una dirección

Sea q un vector unitario. Buscamos el múltiplo aq que más se acerque a x:
$$\min_a\|x-aq\|^2=\|x\|^2-2a q^Tx+a^2.$$
Derivar respecto a a da a=qᵀx. Por tanto:
$$\operatorname{proj}_q(x)=(q^Tx)q.$$
El residuo x−(qᵀx)q es ortogonal a q, porque su producto interno con q vale cero.

Si v no es unitario, la proyección es [(vᵀx)/(vᵀv)]v. Normalizar o incluir el denominador es indispensable.

## 2. Gram–Schmidt paso a paso

Para columnas independientes a₁,a₂:
$$q_1=\frac{a_1}{\|a_1\|},\quad
u_2=a_2-(q_1^Ta_2)q_1,\quad
q_2=\frac{u_2}{\|u_2\|}.$$
Restamos a a₂ su componente paralela a q₁. La independencia asegura u₂≠0 en aritmética exacta.

Ejemplo:
$$a_1=(1,1,0)^T,\quad a_2=(1,0,1)^T.$$
Entonces:
$$q_1=(1,1,0)^T/\sqrt2,\quad q_1^Ta_2=1/\sqrt2,$$
$$u_2=(1/2,-1/2,1)^T,\quad\|u_2\|=\sqrt{3/2},$$
$$q_2=(1,-1,2)^T/\sqrt6.$$
Comprueba q₁ᵀq₂=0 y normas unitarias.

## 3. De las proyecciones a A=QR

Organiza Q=[q₁ q₂] y coeficientes en:
$$R=\begin{pmatrix}\sqrt2&1/\sqrt2\\0&\sqrt{3/2}\end{pmatrix}.$$
Las construcciones anteriores equivalen a:
$$A=QR,\qquad Q^TQ=I.$$
Es una QR reducida: Q tiene dos columnas en ℝ³. QᵀQ=I₂, pero QQᵀ no es I₃; es una proyección de rango dos.

Para más columnas, se sustrae de cada columna su proyección sobre las anteriores y se normaliza. Si aparece un residuo cero, las columnas no eran independientes.

## 4. Resolver mínimos cuadrados

Queremos minimizar ||y−Aβ||². Con A=QR:
$$y-QR\beta=(I-QQ^T)y+Q(Q^Ty-R\beta).$$
Los términos son ortogonales:
$$\|y-A\beta\|^2
=\|(I-QQ^T)y\|^2+\|Q^Ty-R\beta\|^2.$$
El primero no depende de β. El mínimo se obtiene resolviendo el sistema triangular:
$$R\hat\beta=Q^Ty.$$
No hemos formado AᵀA ni su inversa.

Con y=(1,2,3)ᵀ:
$$Q^Ty=(3/\sqrt2,5/\sqrt6)^T.$$
La segunda fila da β₂=5/3. La primera:
$$\sqrt2\beta_1+(1/\sqrt2)(5/3)=3/\sqrt2
\Rightarrow\beta_1=2/3.$$
El residuo es (−4/3,4/3,4/3)ᵀ y su norma al cuadrado es 16/3. Es perpendicular a ambas columnas de A.

## 5. Por qué importa el procedimiento numérico

En norma 2 y con rango columna completo, la condición de AᵀA es el cuadrado de la condición de A. Formar ecuaciones normales puede amplificar dificultades de una matriz ya mal condicionada.

Gram–Schmidt clásico explica bien la geometría, pero puede perder ortogonalidad por redondeo. Las implementaciones suelen preferir transformaciones de Householder, Gram–Schmidt modificado o SVD, según el problema. QR tampoco elimina la falta de información de columnas casi redundantes.

## Ejercicios y soluciones

1. Proyecta (2,3) sobre (1,0): (2,0).
2. Si q es unitario y x⊥q, su proyección es cero.
3. ¿QQᵀ=I siempre que QᵀQ=I? No: si Q es rectangular, proyecta sobre su espacio columna.
4. En el ejemplo, verifica Aβ̂=(7/3,2/3,5/3)ᵀ; restar de y produce el residuo indicado.

**Práctica:** compara QR y ecuaciones normales para datos casi colineales, informando condición y residual; coincidencia en un caso sencillo no garantiza igual estabilidad en todos.
