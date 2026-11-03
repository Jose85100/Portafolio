# Derivación acumulativa — límites de confianza para seleccionar un menú fijo

## Pregunta y alcance

Las extensiones del 29 de octubre al 2 de noviembre seleccionaban alternativas desde probabilidades postuladas o cajas deterministas. Esta iteración cambia explícitamente la pregunta: si esas probabilidades se estimasen mediante conteos binarios, ¿qué opción es de menor costo cuando se exige un límite inferior simultáneo para todo el menú? Los conteos de esta prueba son sintéticos y no representan asistencia observada.

## Fórmula de conteo y adaptación

Para un plan previamente enumerado \(j\), una sesión hipotética tiene indicador \(Y_{ij}\in\{0,1\}\) de que se alcanzó el evento existente (quórum fijo y rol obligatorio presente). Bajo Bernoulli IID con probabilidad constante \(p_j\),

\[
X_j=\sum_{i=1}^{n_j}Y_{ij}\sim\mathrm{Binomial}(n_j,p_j),\qquad \widehat p_j=X_j/n_j.
\]

La estimación puntual \(\widehat p_j\) es el método original de plug-in en esta nueva capa. Con \(m\) opciones, los límites se construyen antes de optimizar costo y el menú se fija antes de mirar \(X_1,\ldots,X_m\). Para error familiar \(\delta\), se asigna \(\alpha=\delta/m\) por opción.

El límite Clopper–Pearson unilateral es la inversión exacta de la prueba binomial:

\[
L_{CP}(x,n,\alpha)=\begin{cases}
0,&x=0,\\
\operatorname{Beta}^{-1}(\alpha;x,n-x+1),&x>0.
\end{cases}
\]

Para \(x>0\), satisface \(\Pr_{p=L}[X\ge x]=\alpha\). Por tanto, \(\Pr_p\{L_{CP}(X,n,\alpha)\le p\}\ge1-\alpha\); la desigualdad suele ser conservadora por la naturaleza discreta de \(X\). Bonferroni aplica la cota de unión:

\[
\Pr(\exists j:L_j>p_j)\le\sum_{j=1}^{m}\alpha_j=\delta,
\]

sin requerir independencia entre las estimaciones de planes. No corrige un menú que se amplía o ajusta después de observar los conteos.

El baseline competitivo Hoeffding recibe el mismo error por plan:

\[
L_H(x,n,\alpha)=x/n-\sqrt{\log(1/\alpha)/(2n)}.
\]

Es deliberadamente la versión no recortada. Un valor negativo es una cota inferior válida sobre una probabilidad y no puede alcanzar una meta \(\tau\ge0\). La selección es \(\arg\min_{j:c_j\,\mathrm{fixed}} c_j\) sujeta a \(L_j\ge\tau\); si el conjunto factible es vacío, el resultado es abstención. Ningún umbral o precio se cambia para obtener una opción factible.

## Oráculo independiente y alcance de exactitud

La fórmula beta de CP se contrasta mediante una bisección separada que suma directamente \(\sum_{k=x}^{n}\binom{n}{k}p^k(1-p)^{n-k}\) y resuelve la igualdad de cola. Además, para una grilla de \((n,p)\), la cobertura exacta se suma sobre toda la distribución binomial, no se infiere de Monte Carlo. “Exacta” aquí describe el oráculo combinatorio bajo el modelo, con aritmética de coma flotante; no es una garantía frente a especificación errónea o parámetros desconocidos fuera del supuesto.

## Propiedades conservadas, perdidas y condiciones

- Se conserva el evento empresarial definido en el historial del programa, el menú sintético, costos abstractos, y las reglas de elegibilidad no modificadas.
- La cota clásica no se modifica algebraicamente. La extensión de ingeniería es envolver el cálculo en una regla de menú y una corrección simultánea auditable.
- Se obtiene cobertura familiar al menos \(1-\delta\) solo si cada serie es binomial IID, los conteos representan el mismo evento y población, y el menú está preespecificado. La validez no depende de independencia entre planes para Bonferroni.
- Si hay deriva temporal, dependencia entre sesiones, selección exploratoria, faltantes informativos o cambio de definición del evento, las garantías binomiales ya no aplican. La simulación de deriva es un contraejemplo explícito a esa premisa.
- Ninguna fórmula estima la calidad, legalidad, imparcialidad, independencia de criterio ni causalidad de decisiones de una junta.

## Resultado previsto a verificar, no conclusión algebraica

Con el menú artificial \((x,n,c)\in\{(110,200,1),(130,200,2),(150,200,3)\}\), \(m=3\), \(\delta=0.05\), y meta \(\tau=0.56\), la predicción falsable es que CP+Bonferroni permite elegir B, mientras Hoeffding con el mismo presupuesto selecciona C. La hipótesis de implementación requiere diferencias inferiores a \(10^{-10}\) frente al oráculo. La grilla exacta y las semillas de simulación son parte de la evidencia reproducible; no constituyen datos empresariales.
