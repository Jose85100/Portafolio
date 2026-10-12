# 04. Espirales de liquidez, margin calls y liquidación forzada

## Hipótesis
Un shock de precios reduce valor de colateral, genera llamadas de margen y fuerza ventas; las ventas deprimen aún más los precios. Este mecanismo de realimentación puede producir respuestas no lineales y umbrales de inestabilidad.

## Modelo de equilibrio local
Sea \(x\ge0\) volumen liquidado y \(p=p_0-\lambda x\), con \(\lambda>0\) impacto lineal local. Si una caída de precios genera requerimiento adicional de caja proporcional a \(m(p_0-p)\), y la entidad debe vender activos para obtener \(x p\) de efectivo, la condición simplificada es

\[
xp=m\lambda x+G_0,
\]

donde \(G_0\) es gap inicial. Sustituyendo \(p=p_0-\lambda x\),

\[
-\lambda x^2+(p_0-m\lambda)x-G_0=0.
\]

La existencia de soluciones reales requiere discriminante

\[
\Delta=(p_0-m\lambda)^2-4\lambda G_0\ge0.
\]

**Advertencia:** la ecuación es un mecanismo didáctico de un activo, no un modelo estructural de clearing; incluso con raíz real, pueden fallar restricciones de inventario, precio positivo, monotonicidad y equilibrio dinámico.

## Dinámica iterativa
Un motor más realista puede actualizar por periodos: pérdidas mark-to-market → margen exigido → caja disponible → volumen de venta → impacto de mercado → nuevo precio. La estabilidad local de un mapa \(x_{t+1}=F(x_t)\) requiere \(|F'(x^\*)|<1\). Si \(|F'(x^\*)|>1\), el punto fijo es inestable bajo iteración local, pero no se demuestra automáticamente colapso del sistema económico.

## Red de contagio
Para instituciones \(i\) y activos \(a\), matrices de tenencias \(H_{ia}\), ventas \(q_{ia}\) y precios \(p_a\), introducir impacto cruzado

\[
\Delta p_a=-\sum_b\Lambda_{ab}\sum_i q_{ib}.
\]

La matriz \(\Lambda\) debe respetar unidades, y su calibración con episodios normales puede fallar bajo ventas sincronizadas. Las conexiones financieras pueden amplificar o absorber shocks; no atribuir causalidad de contagio sin diseño empírico.

## Experimentos
Variar gap inicial, haircut, apalancamiento, profundidad y concentración. Identificar regiones de equilibrio factible, no factible y sensibilidad a reglas de venta. Comparar liquidación proporcional, por menor impacto y por minimización de pérdida total.

## Validación y límites
Verificar conservación de caja y activos, límites de inventario, no negatividad de precios y sensibilidad a paso temporal. La profundidad de mercado es endógena: impacto constante es una aproximación local. El modelo puede apoyar stress testing, no sustituir evidencia de capacidad real de ejecución.
