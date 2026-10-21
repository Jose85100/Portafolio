# Ecuaciones y agenda — ingresos y documentos

Los notebooks ajustan bandas de ingreso corroborado, estudian cobertura y prueban conciliación y sensibilidad a contaminación. Una declaración fuera de banda es una discrepancia, no un fraude confirmado.

## 1. Ingresos cero y modelo en dos partes

**Hipótesis.** Aplicar logaritmo solo a ingresos positivos excluye una población material. Una alternativa propuesta separa ocurrencia y monto:

$$P(I\leq u\mid X)=\pi_0(X)+(1-\pi_0(X))F_+(u\mid X),\quad u>0.$$

Aquí pi0 es probabilidad de ingreso cero y F+ es distribución del ingreso positivo. Un período sin evidencia no se etiqueta automáticamente como ingreso cero.

**Experimento propuesto.** Simular cero estructural, cero temporal y datos faltantes por separado. Comparar log(1+I), un modelo de dos partes y bandas condicionadas a cobertura. Evaluar calibración de pi0, cobertura monetaria por actividad y costo de pedir evidencia adicional.

**Aceptación/refutación.** Verificar que la distribución acumulada sea monótona y su masa cero esté explícita. La cobertura agregada no compensa exclusiones sistemáticas de independientes o negocios nuevos. Si el modelo aprende ausencia del proveedor como ausencia de ingreso, falla el contrato.

## 2. Bandas por segmento y cambios de régimen

**Hipótesis.** Una banda marginal puede ocultar baja cobertura en actividad o período. Se propone estudiar scores de calibración por grupo g:

$$s_i=\max(\hat q_l(X_i)-y_i,y_i-\hat q_u(X_i),0),\quad \hat s_g=Q_{1-\alpha}^{g}(s).$$

La calibración por grupo exige tamaño suficiente e intercambiabilidad dentro del grupo. No garantiza cobertura condicional en cada valor X ni bajo cualquier cambio temporal.

**Experimento propuesto.** Variar el número de positivos de ingreso por actividad y desplazar media/varianza estacional. Comparar ampliación global, por grupo y fallback documentado. Separar selección de grupos, calibración y test; conservar la proporción de casos sin evidencia.

**Aceptación/refutación.** Reportar cobertura, ancho y tamaño por grupo, incluyendo casos donde la banda resulta inútil por amplitud. El notebook ya conserva un contraejemplo bajo desplazamiento: no eliminarlo por no alcanzar la cobertura deseada. Una recalibración posterior necesita un nuevo test.

## 3. Conciliación como grafo de flujos

**Hipótesis.** La consistencia económica mejora al identificar traslados propios y financiación. Para un conjunto de cuentas del mismo titular, se propone separar flujos internos y externos:

$$\Delta B=F_{ext}^{in}-F_{ext}^{out}+F_{financiacion}-F_{servicio\ deuda}.$$

La identidad de caja no demuestra que todas las entradas externas sean ingreso disponible; ventas, reembolsos y capital tienen tratamientos distintos.

**Experimento propuesto.** Generar cuentas enlazadas, transferencias partidas, comisiones y eventos duplicados. Contrastar sumar abonos con conciliación por origen y evidencia. Medir ingreso sobreestimado, partidas sin conciliar y efecto sobre capacidad de pago. La asignación de titularidad y categoría debe conservar incertidumbre.

**Aceptación/refutación.** Un traslado propio no altera el ingreso consolidado; duplicar un evento no cambia saldo; períodos y moneda concilian. Si se necesita mirar una transferencia posterior para aclarar una solicitud anterior, esa aclaración solo puede entrar en un nuevo corte. No se denomina fraude a una partida pendiente.
