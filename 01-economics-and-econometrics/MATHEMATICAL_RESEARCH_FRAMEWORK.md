# Estándar matemático de investigación

## Criterios mínimos para publicar un proyecto como investigación cuantitativa

1. **Formulación:** variables, dimensiones, soporte, información disponible, hipótesis y función objetivo.
2. **Existencia y unicidad:** probar condiciones suficientes o exhibir contraejemplos; en optimización distinguir convexidad estricta, convexidad y no convexidad.
3. **Derivación:** cada ecuación debe provenir de identidad, supuesto, teorema o aproximación etiquetada. Presentar condiciones de primer orden, restricciones y condiciones de segundo orden cuando correspondan.
4. **Identificación:** definir parámetro objetivo y mapa de observables a parámetros; demostrar por qué diferentes parámetros no generan la misma distribución observada, o declarar identificación parcial.
5. **Estimación:** objetivo muestral, regularidad, sesgo, consistencia, distribución límite y estimación de incertidumbre.
6. **Computación:** discretización, error de truncamiento, estabilidad, complejidad, criterio de convergencia y reproducibilidad.
7. **Falsación:** invariantes, casos extremos, pruebas de recuperación, errores de especificación, estabilidad temporal y benchmarks.
8. **Economía aplicada:** mecanismos, efectos de equilibrio general/parcial, interpretación de bienestar y límites de validez externa.

## Ejemplo completo: estimador within de efectos fijos

Supongamos $y_{it}=\alpha_i+\beta x_{it}+u_{it}$, $i=1,\ldots,N$, $t=1,\ldots,T$. Promediando por individuo:
$$
\bar y_i=\alpha_i+\beta\bar x_i+\bar u_i.
$$
Restando ambas expresiones:
$$
\widetilde y_{it}=\beta\widetilde x_{it}+\widetilde u_{it}.
$$
El problema de mínimos cuadrados es $\min_b\sum_{it}(\widetilde y_{it}-b\widetilde x_{it})^2$. Su derivada es $-2\sum_{it}\widetilde x_{it}(\widetilde y_{it}-b\widetilde x_{it})$. Igualándola a cero:
$$
\widehat\beta_{FE}=\frac{\sum_{it}\widetilde x_{it}\widetilde y_{it}}{\sum_{it}\widetilde x_{it}^2}
=\beta+\frac{\sum_{it}\widetilde x_{it}\widetilde u_{it}}{\sum_{it}\widetilde x_{it}^2}.
$$
Con variación within positiva y condiciones de exogeneidad/ley de grandes números apropiadas, el cociente de error converge a cero. Si $x_{it}$ responde a shocks pasados o contemporáneos, la exogeneidad estricta puede fallar. La inferencia requiere tratar correlación intragrupo y el régimen asintótico $(N,T)$.

## Ejemplo completo: varianza mínima de combinación de pronósticos

Para errores $e\in\mathbb R^K$ de media cero y matriz $\Sigma\succ0$, minimizar $w'\Sigma w$ sujeto a $\mathbf1'w=1$. Lagrangiano:
$$
\mathcal L(w,\lambda)=w'\Sigma w-\lambda(\mathbf1'w-1).
$$
FOC: $2\Sigma w-\lambda\mathbf1=0$, por lo que $w=(\lambda/2)\Sigma^{-1}\mathbf1$. Impuesta la restricción:
$$
w^*=\frac{\Sigma^{-1}\mathbf1}{\mathbf1'\Sigma^{-1}\mathbf1}.
$$
Hessiana $2\Sigma\succ0$: óptimo global único. Si se exige $w\ge0$, resolver QP con KKT; si $\Sigma$ es singular, no aplicar la fórmula inversa sin regularización o pseudoinversa y análisis de identificación.

## Nota de madurez

Los 35 documentos `MATHEMATICAL_DERIVATION.md` ofrecen resultados y rutas de derivación específicas, pero **no equivalen todavía a monografías exhaustivas** con demostración de todos los teoremas, estimadores especializados y código calibrado. Se deben ampliar individualmente y vincular a notebooks propios.
