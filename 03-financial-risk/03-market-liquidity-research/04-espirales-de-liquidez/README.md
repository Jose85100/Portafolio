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

## Evidencia observada disponible

El companion [Concentración observada de tenedores TES](observed-tes-holder-concentration/README.md) calcula concentración de las 21 categorías publicadas de tenedor en frecuencia mensual, 2010–2025. Aporta contexto sobre la concentración agregada de la base inversora, una dimensión potencial de exposición común. La categoría publicada no identifica tenedores finales ni sus incentivos o ventas coordinadas. Estos datos no observan transacciones, profundidad o respuesta de precios: no calibran \(\lambda\), ni validan el mecanismo de espiral descrito arriba. Para ello se requiere grano tenedor × emisión × fecha, posiciones disponibles y comprometidas, y operaciones con precio y cantidad alrededor de episodios de estrés.

Una medida más cercana a actividad transada está disponible en el companion [Actividad y concentración de compraventas SEN](../../../04-quant-strategy-and-products/market-microstructure/sen-cash-concentration/README.md), con el resumen oficial de cierres de BanRep para septiembre de 2026. Sus 1.294 filas resumen fecha × especie × rueda × plazos; al aislar la rueda CONH (compraventa con cumplimiento el mismo día), se obtienen valor reportado en pesos y concentración diaria por especie para 22 fechas. La mediana diaria reportada fue COP 2.594,9 miles de millones y el HHI de la actividad por especie tuvo mediana 1.299. Es evidencia de actividad y concentración negociada en un mes; no es una serie de profundidad disponible, spread, impacto de precio, ventas forzadas ni una calibración de \(\lambda\). La página del companion detalla su grano, hash, reproducción y límites.

### Brecha para medir profundidad e impacto de liquidación

La ficha consultada de cierres SEN cubre solo septiembre de 2026 y agrega resultados por fecha, especie, rueda y plazos. No publica cotizaciones bid/ask sincronizadas, cantidades disponibles a distintos niveles del libro, hora de cada operación, dirección agresora ni secuencia de transacciones con precio y cantidad. Por eso no se puede observar el costo de ejecutar una venta ni estimar una curva precio–cantidad a través del tiempo. El siguiente insumo requerido es un panel por especie y marca temporal, con bid, ask, profundidad acumulada, operaciones ejecutadas (precio, cantidad y hora) y varios meses que incluyan episodios de tensión. Para interpretar ventas forzadas se debe vincularlo con posiciones líquidas libres de gravamen y montos de venta por tenedor. Hasta obtener ese grano, la evidencia SEN sirve para describir actividad mensual reportada, mientras que \(\lambda\) permanece como parámetro de escenario del laboratorio.


## Recursos relacionados

El [laboratorio integrado](../laboratorio-integrado/README.md) reúne simulaciones, notebook y pruebas comunes de mercado y liquidez. Es un ejemplo sintético relacionado; no implementa necesariamente el modelo completo formulado en esta página.
