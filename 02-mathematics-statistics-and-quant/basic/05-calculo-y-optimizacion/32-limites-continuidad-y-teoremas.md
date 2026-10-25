# 32. Límites y continuidad: definiciones y garantías

**Pregunta:** ¿qué significa exactamente acercarse a un valor?  
**Objetivo:** usar ε–δ y distinguir existencia de una raíz, de un extremo y de una derivada. **Antes:** desigualdades y funciones.

## 1. Definición ε–δ

Escribimos limₓ→ₐf(x)=L si para todo ε>0 existe δ>0 tal que:
$$0<|x-a|<\delta\Rightarrow|f(x)-L|<\varepsilon.$$
Primero se fija una tolerancia de salida ε y luego se elige una tolerancia de entrada δ que la garantice. La exclusión 0<|x−a| significa que el valor exacto f(a) no decide el límite.

Para f(x)=3x+2 cerca de a=1:
$$|f(x)-5|=3|x-1|.$$
Dado ε>0, escoger δ=ε/3 demuestra el límite 5.

## 2. Ejemplo no lineal

Queremos probar limₓ→₂x²=4. Factoriza:
$$|x^2-4|=|x-2||x+2|.$$
Necesitamos controlar el segundo factor. Si |x−2|<1, entonces 1<x<3 y |x+2|<5. Por tanto:
$$|x^2-4|<5|x-2|.$$
Elegimos δ=min(1,ε/5). Así ambas condiciones se cumplen y el error de salida es menor que ε. La elección no es única; basta una que funcione.

Esta técnica de restringir primero un entorno y luego acotar un factor aparece en muchas pruebas de continuidad.

## 3. Continuidad y discontinuidades

f es continua en a si está definida en a y limₓ→ₐf(x)=f(a). Para:
$$f(x)=\frac{x^2-1}{x-1},\quad x\ne1,$$
el límite en 1 es 2, pero falta f(1). Definir f(1)=2 elimina la discontinuidad. Definir f(1)=7 no lo hace.

En 1/x cerca de cero, los límites laterales divergen con signos opuestos; no hay un límite real finito ni una extensión continua.

## 4. Teorema del valor intermedio

Si f es continua en [a,b] y f(a),f(b) tienen signos opuestos, existe c∈(a,b) con f(c)=0. No garantiza una única raíz.

Para f(x)=x³−x−1:
$$f(1)=-1,\quad f(2)=5.$$
Hay al menos una raíz entre 1 y 2. Como f'=3x²−1>0 en [1,2], la función es estrictamente creciente allí y la raíz en ese intervalo es única. La existencia usó continuidad; la unicidad usó monotonía.

Sin continuidad, el cambio de signo puede ser un salto que nunca pase por cero.

## 5. Extremos y derivadas: otros dos teoremas

Una función continua en un intervalo cerrado y acotado alcanza máximo y mínimo. La condición de cerrado importa: f(x)=x en (0,1) es acotada pero no alcanza sus extremos.

El teorema del valor medio requiere continuidad en [a,b] y derivabilidad en (a,b); garantiza c con:
$$f'(c)=\frac{f(b)-f(a)}{b-a}.$$
Para x² en [1,3], la pendiente secante es (9−1)/2=4, igual a f'(2)=4.

Estos teoremas se presentan con sus hipótesis; no se demuestra aquí su versión general.

## Ejercicios y soluciones

1. Para probar limₓ→₀5x=0, sirve δ=ε/5.
2. ¿|x| es continua en cero? Sí. ¿Derivable? No: pendientes laterales −1 y 1.
3. ¿La continuidad garantiza un máximo en ℝ? No: x² no tiene máximo.
4. ¿Un cambio de signo de 1/x entre −1 y 1 garantiza raíz? No: la función no es continua en todo ese intervalo.

**Error frecuente:** aplicar un teorema por su conclusión deseada sin comprobar antes todas sus hipótesis.
