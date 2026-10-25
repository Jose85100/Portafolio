# 39. Cadenas de Markov: transición y distribución estacionaria

**Pregunta:** ¿cómo evolucionan probabilidades entre estados?  
**Objetivo:** construir una matriz estocástica, hallar un equilibrio probabilístico y distinguirlo de convergencia. **Antes:** probabilidad y matrices.

## 1. Declarar estados y convención

Una cadena de Markov homogénea satisface:
$$P(X_{t+1}=j\mid X_t=i,X_{t-1},\ldots)=P_{ij},$$
con probabilidades que no dependen de t. La propiedad dice que el estado actual resume la información del pasado relevante para la siguiente transición; es un supuesto que debe evaluarse.

Usaremos vectores fila de probabilidades. Las filas de P suman uno y contienen valores no negativos:
$$\pi_{t+1}=\pi_tP.$$
Otras convenciones usan columnas; mezclar ambas produce errores de orientación.

## 2. Un ejemplo de dos estados

Sean estados A y B:
$$P=\begin{pmatrix}0.9&0.1\\0.2&0.8\end{pmatrix}.$$
Si π₀=(1,0), entonces π₁=(0.9,0.1), y:
$$\pi_2=(0.9,0.1)P=(0.83,0.17).$$
La probabilidad de estar en B tras dos pasos combina A→A→B y A→B→B:
$$0.9(0.1)+0.1(0.8)=0.17.$$
Elevar P a t incorpora todos los caminos de longitud t mediante suma y producto de probabilidades condicionales.

## 3. Resolver la distribución estacionaria

Buscamos π*=π*P con π*=(q,1−q):
$$q=0.9q+0.2(1-q)=0.7q+0.2.$$
Así q=2/3 y:
$$\pi^*=(2/3,1/3).$$
La distribución estacionaria permanece igual si se usa como distribución inicial. No significa que cada individuo se quede en un estado fijo.

## 4. Demostrar convergencia en este ejemplo

Sea qₜ=P(Xₜ=A). La recurrencia es:
$$q_{t+1}=0.7q_t+0.2.$$
Restar q*=2/3:
$$q_{t+1}-2/3=0.7(q_t-2/3).$$
Por inducción:
$$q_t=\frac23+0.7^t\left(q_0-\frac23\right).$$
Como |0.7|<1, converge para cualquier distribución inicial. Este argumento prueba convergencia para el ejemplo, sin necesidad de usar un teorema general de cadenas.

## 5. Estacionariedad no implica convergencia desde todo inicio

Para P=[[0,1],[1,0]], π*=(1/2,1/2) es estacionaria, pero desde (1,0) se alterna entre (1,0) y (0,1). Es una cadena periódica.

En cadenas finitas, irreducibilidad y aperiodicidad garantizan una única distribución estacionaria y convergencia a ella. Aquí se cita el teorema; no se demuestra su versión general. Si hay clases cerradas distintas, puede haber varias distribuciones estacionarias.

## 6. Estado absorbente

Con:
$$P=\begin{pmatrix}0.8&0.2\\0&1\end{pmatrix},$$
B es absorbente: una vez allí, no se sale. Desde A, la probabilidad de seguir en A después de t pasos es 0.8ᵗ; la de haber llegado a B es 1−0.8ᵗ.

Si T es el paso del primer ingreso a B, tiene distribución geométrica con p=0.2 y E[T]=5, bajo este modelo homogéneo.

## Ejercicios y soluciones

1. Verifica π*P=π* en el primer ejemplo: (2/3·0.9+1/3·0.2,2/3·0.1+1/3·0.8)=(2/3,1/3).
2. En el ejemplo absorbente, P(T≤3)=1−0.8³=0.488.
3. ¿Una fila (0.4,0.4) es válida sin estados adicionales? No: suma 0.8.
4. ¿Observar transiciones permite asumir homogeneidad futura? No: cambios de régimen y composición pueden alterar las probabilidades.

**Aplicación:** migraciones de calificación y estados operativos. Definir estados y horizonte precede a estimar la matriz; los números de esta lección son exclusivamente didácticos.
