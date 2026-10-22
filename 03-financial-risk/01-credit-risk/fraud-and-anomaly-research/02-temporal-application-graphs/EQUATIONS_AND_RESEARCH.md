# Ecuaciones y agenda — redes temporales

## Estado después de la ampliación

Los notebooks ya ejecutan comparación individual/red, cobertura nominal y por escenarios, y eficacia parcial bajo supuestos. El decaimiento temporal propuesto, los efectos causales de contención y una GNN siguen pendientes.

Los notebooks implementan conteos disponibles al corte y cobertura conjunta de pérdida en un pequeño problema exacto. No entrenan una GNN ni validan campañas reales.

## 1. Vínculos inciertos y cobertura robusta

**Hipótesis.** Resolver la asignación con un solo grafo puede sobrevalorar vínculos de baja confianza. Sea $A^{(s)}_{ij}$ la cobertura de exposición j por acción i en escenario s. Se propone:

$$\max_x\min_s\left(\sum_j\ell_jz_{js}-\sum_i c_ix_i\right),\qquad z_{js}\leq\sum_i A^{(s)}_{ij}x_i.$$

**Experimento propuesto.** Partir del contraejemplo del notebook 02 y agregar escenarios con enlaces falsos, perdidos y tardíos. Comparar solución nominal y robusta con el mismo presupuesto, registrando beneficio por escenario y pérdida de eficiencia nominal. El generador debe incluir hogares y centros de atención legítimos.

**Aceptación/refutación.** La cobertura no puede contar una exposición dos veces ni superar su pérdida prevenible. Enumerar problemas pequeños como oráculo. Si la protección depende de escenarios que eliminan todos los casos difíciles, la conclusión no es útil. El máximo entre escenarios no certifica protección ante un grafo no considerado.

## 2. Decaimiento temporal y nueva campaña

**Hipótesis.** La novedad de vínculos puede complementar el grado. Una agregación propuesta es:

$$R_i(t)=\sum_{j:e_{ij}<t,\ a_{ij}\leq t}\frac{\exp(-(t-e_{ij})/\tau)}{\log(2+D_j(t))}.$$

**Experimento propuesto.** Evaluar ventanas 1/7/30 días y varios valores de tau fijados en validación. Contrastar expansión rápida de una campaña contra uso estable de una entidad legítima. Separar la evaluación temporal operativa de una prueba de campañas nuevas. No usar grados retrospectivos ni etiquetas de vecinos confirmadas después del corte.

**Aceptación/refutación.** Agregar aristas futuras debe dejar intacta toda salida anterior. La métrica principal será aporte incremental a igual presupuesto y fricción en hubs legítimos. Si el ranking solo refleja el tamaño de la entidad o penaliza infraestructura compartida, revisar la hipótesis antes de añadir una red neuronal.

## 3. Prevención compartida y causalidad

**Hipótesis.** Investigar un nodo puede contener otros, pero el efecto de dos acciones puede solaparse o complementarse. Bajo éxitos independientes, una aproximación es:

$$q_j(S)=1-\prod_{i\in S}(1-q_{ij}).$$

La fórmula no es válida por definición: independencia, cobertura y dirección del efecto deben justificarse. Dos revisiones sobre el mismo origen pueden ser totalmente redundantes; otras acciones pueden requerirse conjuntamente.

**Experimento propuesto.** Comparar redundancia total, independencia y complementariedad en redes pequeñas. Enumerar políticas y contrastar con cobertura perfecta. En un piloto institucional, medir efectos al nivel de campaña y conservar el momento de contención para no atribuir prevención a pérdidas ya desembolsadas.

**Aceptación/refutación.** Los beneficios esperados se concilian por flujo/caso y nunca se suman como saldos independientes sin revisar vínculos. Si el efecto compartido no es identificable con la evidencia disponible, reportar rangos y conservar la política individual como baseline; no imputar eficacia perfecta.
