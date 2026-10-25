# 2. Funciones: relaciones, gráficas y escalas

**Prerrequisito:** álgebra. **Objetivo:** interpretar dominio, pendiente, composición e inversa.

## Una entrada, una salida

Una función asigna a cada entrada de su dominio exactamente una salida. En $C(q)=100+2q$, $q\ge0$ representa unidades producidas y $C$ el costo monetario. El dominio económico puede ser menor que el dominio algebraico: cantidades negativas no tienen sentido en este ejemplo.

La pendiente entre dos puntos es $\Delta C/\Delta q$. Aquí siempre vale 2 unidades monetarias por unidad producida. El intercepto 100 representa costo fijo. La gráfica es una recta que pasa por $(0,100)$, $(10,120)$ y $(20,140)$: ubica esos puntos y únelos.

## Rectas, curvas y geometría

En $y=a+bx$, $b$ es pendiente y $a$ intercepto. Dos rectas con pendientes distintas se cruzan una vez. Si ingreso $I(q)=5q$, el punto de equilibrio satisface $5q=100+2q$, por lo que $q=100/3$. Si solo se venden unidades enteras, 34 es la primera cantidad con beneficio no negativo.

Una cuadrática se entiende completando el cuadrado:
$$x^2-4x+3=(x-2)^2-1.$$
La parábola abre hacia arriba; tiene vértice $(2,-1)$ y raíces 1 y 3. El cuadrado nunca es negativo, de modo que el mínimo es $-1$.

La distancia euclidiana entre $(x_1,y_1)$ y $(x_2,y_2)$ es $\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$, por Pitágoras. Su interpretación exige escalas comparables; mezclar pesos y años sin ajustar unidades puede producir distancias poco útiles.

## Componer e invertir

Si $g(x)=x+1$ y $f(x)=x^2$, entonces $f(g(x))=(x+1)^2$, mientras $g(f(x))=x^2+1$. El orden importa.

Una inversa deshace una función. Para $y=3x+2$, despejar da $x=(y-2)/3$; por ello $f^{-1}(y)=(y-2)/3$. $x^2$ no tiene inversa en todo $\mathbb R$: $2$ y $-2$ dan 4. Restringiendo a $x\ge0$, su inversa es $\sqrt{x}$.

## Ejercicios

1. Encuentra dominio real de $\sqrt{x-2}$ y $\ln(x-2)$.
2. Calcula el vértice y las raíces de $x^2-6x+8$.
3. ¿Una relación observada entre ingreso y consumo demuestra causalidad?

## Soluciones

1. Raíz: $x\ge2$. Logaritmo: $x>2$.
2. $(x-3)^2-1$: vértice $(3,-1)$; raíces 2 y 4.
3. No. Puede haber variables omitidas, simultaneidad o selección. Una función descriptiva no identifica por sí misma un efecto causal.

**Error frecuente:** interpretar «creciente» como «lineal». $x^2$ crece en $x\ge0$, pero su pendiente cambia.
