# Ecuaciones y agenda — identidad y KYC

## Estado después de la ampliación

Dependencia parcial y EVSI/EVPI ya tienen experimentos ejecutados dentro de los notebooks. La calibración jerárquica por proveedor y la estimación con evidencia institucional siguen pendientes.

Los dos notebooks de esta carpeta ejecutan Bayes, calibración y asignación económica. Las tres extensiones siguientes son ideas formuladas, aún sin ajustar sobre datos reales.

## 1. Dependencia entre fuentes y evidencia incremental

**Hipótesis.** Una fuente adicional aporta información solo si no es una copia del origen ya observado. La actualización exacta de odds requiere la razón conjunta:

$$O(Y\mid E_1,E_2)=O(Y)\frac{P(E_1,E_2\mid Y=1)}{P(E_1,E_2\mid Y=0)}.$$

La aproximación de producto de razones marginales necesita independencia condicional. El notebook 01 presenta el extremo de dependencia total y demuestra el exceso de confianza.

**Experimento propuesto.** Simular dependencia de 0 a 1 manteniendo prevalencia y sensibilidad marginal aproximadamente constantes. Comparar producto marginal, logit con interacción y estimación conjunta regularizada. Separar clientes y versiones de proveedor entre ventanas. Conservar la genealogía de evidencia para distinguir coincidencia informativa de réplica técnica.

**Aceptación/refutación.** Exigir menor Brier/log loss fuera de muestra y calibración en positivos de evidencia, no solo mayor AP. Si la mejora desaparece al separar proveedores o surge solo de conocer un resultado posterior, rechazarla. Incertidumbre por cohorte y pocos estados observados impiden estimar libremente todas las tablas conjuntas.

## 2. Valor de información de una verificación

**Hipótesis.** Una verificación puede valer por cambiar la decisión posterior, incluso si ella misma no previene pérdida. Para un resultado futuro $Z$:

$$EVSI=\min_a E[C(a)\mid X]-E_Z[\min_a E[C(a)\mid X,Z]]-c_Z.$$

La expectativa de Z debe reflejar resultados positivos, negativos e inconclusos. No confundir este valor de información con el parámetro de eficacia q del motor actual.

**Experimento propuesto.** Definir una prueba sintética con sensibilidad, especificidad y costo; actualizar el posterior con cada resultado y resolver de nuevo la decisión. Comparar verificar a todos, a nadie y según EVSI bajo presupuesto. Variar dependencia con evidencia inicial y tasa de inconclusos. Los tiempos de espera y el abandono legítimo tendrán costo separado.

**Aceptación/refutación.** Conciliar costo antes y después por enumeración de todos los resultados. Si el beneficio depende de tratar resultados inconclusos como legítimos o positivos perfectos, la formulación falla. En datos institucionales, estimar parámetros fuera del conjunto que selecciona la política.

## 3. Calibración local con información escasa

**Hipótesis.** Una tasa por proveedor o producto puede necesitar contracción hacia una población común, evitando calibradores inestables. Una formulación propuesta es:

$$\operatorname{logit}(p_{ig})=a_g+b_g\operatorname{logit}(\hat p_i),\quad a_g\sim N(a_0,\tau_a^2).$$

**Experimento propuesto.** Comparar calibración global, por grupo y jerárquica con 5/20/100 positivos por grupo; reservar una cohorte posterior y grupos nuevos. Reportar Brier, pendiente/intercepto de calibración, cobertura de fuentes y costo económico de la política congelada.

**Aceptación/refutación.** Mejorar la ventana de calibración no basta: exigir estabilidad posterior e intervalos coherentes. Si una fuente está ausente, activar una ruta de calidad en vez de imputar una validación exitosa. El ejemplo ejecutado enseña el riesgo de balanceo y calibración; este modelo jerárquico todavía no está implementado.
