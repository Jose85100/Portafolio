# 19. Covarianza y esperanza condicional

**Objetivo:** derivar la varianza de una suma y separar variación interna de diferencias entre grupos.  
**Prerrequisitos:** probabilidad, momentos y álgebra lineal. **Pregunta guía:** ¿qué información pierde un promedio agregado?

## 1. La covarianza desde la definición

Si X e Y tienen segundos momentos finitos:
$$\operatorname{Cov}(X,Y)=E[(X-\mu_X)(Y-\mu_Y)].$$
Expandir y usar linealidad da:
$$\operatorname{Cov}(X,Y)=E[XY]-E[X]E[Y].$$
Es positiva cuando valores superiores a sus medias suelen ocurrir juntos; negativa cuando tienden a ir en direcciones opuestas. Su magnitud depende de unidades.

La correlación divide por desviaciones estándar positivas:
$$\rho=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\sigma_Y}.$$
Si una variable es constante, su varianza es cero y esta expresión no está definida. La cota |ρ|≤1 se deriva de Cauchy–Schwarz, no es un supuesto adicional.

## 2. Derivar la varianza de una combinación

Para Z=aX+bY:
$$Z-E[Z]=a(X-\mu_X)+b(Y-\mu_Y).$$
Elevar al cuadrado y tomar esperanza:
$$
\operatorname{Var}(Z)=a^2\sigma_X^2+b^2\sigma_Y^2
+2ab\operatorname{Cov}(X,Y).
$$
Con pesos 1/2, varianzas 0.04 y 0.09, y covarianza 0.01:
$$\operatorname{Var}(Z)=0.25(0.04)+0.25(0.09)+0.5(0.01)=0.0375.$$
Omitir el término cruzado daría 0.0325: otro resultado.

Independencia implica covarianza cero bajo estos momentos, pero la recíproca es falsa.

## 3. Contraejemplo: dependencia sin correlación

Sea X uniforme en [−1,1] y Y=X². Entonces E[X]=0 y:
$$E[XY]=E[X^3]=0$$
por simetría. Por ello Cov(X,Y)=0. Sin embargo, conocer X determina Y exactamente: no son independientes. La covarianza resume dependencia lineal, no todas las formas de dependencia.

## 4. Promediar promedios con los pesos correctos

Si G identifica grupos, E[X|G=g] es la media dentro del grupo. Para grupos discretos:
$$E[X]=\sum_gP(G=g)E[X\mid G=g].$$
Es la ley de la esperanza total: descomponemos el conjunto de resultados en grupos y ponderamos por sus probabilidades, no damos el mismo peso a grupos de tamaños distintos.

**Ejemplo sintético.** Dos grupos tienen pesos 0.8 y 0.2, medias 10 y 20, y varianzas internas 4 y 9. La media total es 0.8·10+0.2·20=12.

## 5. Derivar la varianza total

Escribe m(G)=E[X|G] y μ=E[X]:
$$X-\mu=(X-m(G))+(m(G)-\mu).$$
Al elevar al cuadrado aparece un término cruzado. Su esperanza es cero porque:
$$E[X-m(G)\mid G]=0.$$
Por tanto:
$$
\operatorname{Var}(X)=E[\operatorname{Var}(X\mid G)]
+\operatorname{Var}(E[X\mid G]).
$$
En el ejemplo:
$$E[\operatorname{Var}(X\mid G)]=0.8(4)+0.2(9)=5,$$
$$\operatorname{Var}(m(G))=0.8(10-12)^2+0.2(20-12)^2=16.$$
La varianza total es 21. Promediar solo las varianzas internas omite las diferencias de nivel entre grupos.

## Ejercicios y soluciones

1. Si Cov(X,Y)=0, ¿Var(X+Y)=Var(X)+Var(Y)? Sí, si los segundos momentos son finitos; no necesitas independencia.
2. ¿La media simple de 10 y 20 describe la población anterior? No: 15 ignora los pesos; la correcta es 12.
3. Si todos los grupos tienen igual media, ¿desaparece el segundo término de la varianza total? Sí, porque m(G) es constante.
4. ¿Correlación cero descarta una relación no lineal? No: Y=X² es el contraejemplo.

**Aplicación:** segmentación de cartera y atribución de dispersión. La descomposición describe fuentes estadísticas; no identifica efectos causales.
