# 24. Actualización bayesiana: modelo Beta–Bernoulli

**Objetivo:** derivar una posterior, interpretar sus componentes y distinguir media posterior de máxima verosimilitud.  
**Prerrequisitos:** Bayes, densidades y estimación. **Pregunta guía:** ¿cómo se combina información previa con observaciones sin ocultar los supuestos?

## 1. Declarar el modelo

Suponemos Xᵢ|p IID Bernoulli(p). El parámetro p es desconocido y le asignamos una distribución previa Beta(α,β), con α,β>0:
$$\pi(p)=\frac{p^{\alpha-1}(1-p)^{\beta-1}}{B(\alpha,\beta)},\quad0<p<1.$$
La constante:
$$B(\alpha,\beta)=\int_0^1p^{\alpha-1}(1-p)^{\beta-1}dp$$
normaliza la densidad. α y β son elecciones explícitas de modelación; no son datos observados.

## 2. Multiplicar y normalizar

Con k éxitos en n observaciones, la verosimilitud es proporcional a pᵏ(1−p)ⁿ⁻ᵏ. Bayes implica:
$$
\pi(p\mid x)\propto
p^k(1-p)^{n-k}p^{\alpha-1}(1-p)^{\beta-1}.
$$
Sumar exponentes:
$$\pi(p\mid x)\propto p^{\alpha+k-1}(1-p)^{\beta+n-k-1}.$$
Reconocemos una densidad Beta:
$$p\mid x\sim\operatorname{Beta}(\alpha+k,\beta+n-k).$$
La palabra «conjugada» significa que la posterior pertenece a la misma familia que la previa, no que los supuestos sean necesariamente correctos.

## 3. Derivar la media de una Beta

Si P~Beta(a,b):
$$
E[P]=\frac1{B(a,b)}\int_0^1p^a(1-p)^{b-1}dp
=\frac{B(a+1,b)}{B(a,b)}=\frac a{a+b}.
$$
La última identidad puede obtenerse usando B(a,b)=Γ(a)Γ(b)/Γ(a+b) y Γ(a+1)=aΓ(a). De modo similar:
$$E[P^2]=\frac{a(a+1)}{(a+b)(a+b+1)},$$
y restar E[P]² da:
$$\operatorname{Var}(P)=\frac{ab}{(a+b)^2(a+b+1)}.$$

## 4. La media posterior como combinación ponderada

Para n>0:
$$
E[p\mid x]=\frac{\alpha+k}{\alpha+\beta+n}
=\frac{\alpha+\beta}{\alpha+\beta+n}\frac{\alpha}{\alpha+\beta}
+\frac{n}{\alpha+\beta+n}\frac{k}{n}.
$$
Es una combinación entre media previa y frecuencia observada. α+β actúa como concentración o peso equivalente de la previa en esta identidad; llamarlo conteo real de observaciones sería engañoso.

**Ejemplo:** previa Beta(2,8), n=20, k=4. La previa tiene media 0.2 y la posterior es Beta(6,24), también de media 0.2:
$$\operatorname{Var}(p\mid x)=\frac{6\cdot24}{30^2\cdot31}=\frac4{775}\approx0.0051613.$$
La media no cambia porque los datos coinciden con la proporción previa; la incertidumbre sí cambia.

## 5. Predicción y estimación son distintas preguntas

Para una siguiente observación del mismo mecanismo:
$$P(X_{n+1}=1\mid x)=E[p\mid x].$$
Esto se obtiene integrando p respecto de la posterior.

Con cero éxitos en 20 y previa Beta(2,8), la posterior es Beta(2,28) y la probabilidad predictiva es 2/30≈0.0667. El estimador ML sería cero. La diferencia no es un error aritmético: responde a incluir una previa.

## Ejercicios con solución

1. Con previa Beta(1,1), n=10 y k=3, la posterior es Beta(4,8); media 1/3.
2. ¿Un intervalo creíble del 95% tiene la misma interpretación que uno frecuentista? No: asigna probabilidad posterior al parámetro, condicionada al modelo, previa y datos.
3. ¿Qué pasa si cambia el mecanismo generador de datos? La hipótesis de p común puede fallar; acumular observaciones antiguas sin revisar estabilidad puede ser inapropiado.
4. ¿Basta una sola previa? Conviene comparar previas justificables: si las conclusiones cambian mucho, esa sensibilidad es parte del resultado.

**Límite:** el modelo es didáctico. Dependencia entre observaciones, selección y heterogeneidad pueden requerir modelos jerárquicos u otra verosimilitud.
