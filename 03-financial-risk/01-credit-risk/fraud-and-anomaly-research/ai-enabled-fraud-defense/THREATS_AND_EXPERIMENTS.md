# Amenazas y agenda de experimentos

Estas 16 ideas son diseños falsables. Los ataques se describen para defensa y evaluación autorizada; no se incluyen instrucciones operativas para evadir controles. Solo las ideas 03 y 13 tienen experimentos acotados nuevos en el notebook. Los demás diseños requieren datos, implementación y validación.

Arquitecturas: A=KYC; B=documentos; C=sesión/desembolso; D=red y vigilancia. Fuentes en [sources.json](sources.json); las fórmulas no citadas como reproducción son definiciones o propuestas propias.

## 01. Separar presentación, inyección y rostro · A

**Hipótesis:** Un baseline documental/facial puede aceptar un medio introducido fuera de la cámara. Medir familias por separado evita esconder una vía débil en el promedio.

**Modelos y usos:** Reglas de calidad + verificación facial; challenger con integridad de captura e inyección.

**Cantidad a medir:**

```text
ASR_k = ataques aceptados de familia k / ataques evaluados de familia k
```

**Datos y contraste:** Corpus autorizado de ataques controlados y capturas genuinas; separar dispositivo, identidad y herramienta entre desarrollo/test. IC por familia y rechazo genuino.

**Criterio para descartar:** Descartar si mejora promedio pero empeora una familia crítica o excluye genuinos sin alternativa.

**Base:** S:nist; S:ffpp.

## 02. Generalización a generadores no vistos · A

**Hipótesis:** Un detector puede aprender artefactos de compresión del dataset, no fraude generalizable.

**Modelos y usos:** Detector supervisado con partición aleatoria frente a leave-one-generator/device-out.

**Cantidad a medir:**

```text
Gap_k = TPR_in - TPR_unseen,k, con FPR fijado en desarrollo
```

**Datos y contraste:** Congelar umbral y evaluar manipulación, compresión y cámara nunca vistas; separar persona entre particiones. No entrenar con el test.

**Criterio para descartar:** Descartar generalización si el intervalo del gap supera la tolerancia acordada; reportar condiciones sin soporte.

**Base:** S:ffpp; diseño propio.

## 03. Dependencia entre controles · A

**Hipótesis:** Dos controles con el mismo fallo compartido reducen menos riesgo que bajo independencia.

**Modelos y usos:** Producto de tasas marginales frente a tasa conjunta observada.

**Cantidad a medir:**

```text
P(A y B | F) = P(A|F) P(B|A,F)
```

**Datos y contraste:** Medir fallos en pares sobre los mismos ataques y versiones; bootstrap por familia/identidad. Notebook simula dependencia, no evalúa productos.

**Criterio para descartar:** Descartar el argumento de independencia si la tasa conjunta supera materialmente el producto y cambia la decisión de costo.

**Base:** Experimento propio; notebook.

## 04. Valor incremental de proveedor · A

**Hipótesis:** La compra solo aporta si la señal nueva mejora la acción al mismo presupuesto.

**Modelos y usos:** Baseline interno congelado frente a baseline + señal externa, recalibrados en ventana separada.

**Cantidad a medir:**

```text
Delta C = mean(C_base - C_nuevo) - costo_incremental_por_caso
```

**Datos y contraste:** Mismo test temporal, mismo menú de acciones/capacidad y costo por todos los intentos. Bootstrap pareado por incidente/red.

**Criterio para descartar:** Descartar si la cota inferior del beneficio no supera el costo o si suben daño/fricción fuera de guardrails predefinidos.

**Base:** Diseño propio; motor económico existente.

## 05. Identidad sintética con poca historia · A

**Hipótesis:** Falta de huella y evidencia contradictoria tienen semánticas distintas.

**Modelos y usos:** Reglas transparentes frente a logit/boosting con indicadores de cobertura y fuente.

**Cantidad a medir:**

```text
logit(p_i) = beta_0 + beta_x x_i + beta_m m_i
```

**Datos y contraste:** Adjudicar identidades nuevas legítimas, robadas y sintéticas; evaluar por canal/antigüedad. No etiquetar automáticamente ausencia como fraude.

**Criterio para descartar:** Descartar señal si solo captura exclusión de población sin cobertura y no mejora costo fuera de muestra.

**Base:** S:fed; S:socure.

## 06. Grafo temporal contra granjas de solicitudes · D

**Hipótesis:** Una red compartida puede ser fraude coordinado o infraestructura legítima.

**Modelos y usos:** Conteos por entidad/ventana frente a GNN temporal con tipo de relación.

**Cantidad a medir:**

```text
N_e(t)=sum_j 1[e en caso_j, event_j<t, available_j<=t]
```

**Datos y contraste:** Agrupar componentes y tiempo en splits; usar alias de dispositivo con caducidad y evitar contar solicitud actual. Medir hogares/cibercafés legítimos.

**Criterio para descartar:** Descartar GNN si no supera conteos al mismo costo o si enlaces benignos dominan las alertas.

**Base:** S:care; especialista temporal existente.

## 07. Resistencia al camuflaje de vecinos · D

**Hipótesis:** Agregar relaciones benignas puede diluir evidencia del nodo.

**Modelos y usos:** Agregación indiscriminada frente a selección de vecinos o conteos robustos.

**Cantidad a medir:**

```text
Delta_k = score(G con k enlaces benignos) - score(G)
```

**Datos y contraste:** Perturbar solo el grafo sintético autorizado; mantener corte, nodos de test y etiquetas. Evaluar sensibilidad a vecinos falsos y censurados.

**Criterio para descartar:** Descartar si pequeñas perturbaciones benignas invierten masivamente acciones o si el challenger no mejora robustez.

**Base:** S:care; propuesta, no réplica del paper.

## 08. Documento que dice más de lo que demuestra · B

**Hipótesis:** Un span literal puede ser semánticamente incorrecto como ingreso.

**Modelos y usos:** OCR/extracción con span frente a extractor + clasificador de concepto + conciliación.

**Cantidad a medir:**

```text
precision_soporte = campos respaldados / campos afirmados
```

**Datos y contraste:** Corpus adjudicado con salario, préstamo, transferencia propia, negación, corrección y paráfrasis. Separar plantillas y emisores.

**Criterio para descartar:** Descartar automatización si sube exactitud lexical pero falla soporte o titularidad en casos críticos.

**Base:** Pipeline documental existente; diseño propio.

## 09. Conciliación robusta de ingresos · B

**Hipótesis:** Un residuo grande puede indicar error de período, ingreso irregular o alteración; requiere verificación.

**Modelos y usos:** Reglas de período/moneda frente a residuo robusto y modelo cuantílico.

**Cantidad a medir:**

```text
r_i = (ingreso_declarado_i - mediana_referencia_i) / max(MAD_i, epsilon)
```

**Datos y contraste:** Conciliar titular, período, recurrencia y categoría; datos de fuente conectada con autorización; epsilon en unidades monetarias. Validar independientes y asalariados por separado.

**Criterio para descartar:** Descartar umbral universal si produce falsas alertas sistemáticas por ocupación o histórico incompleto.

**Base:** S:belvo-doc; especialista de ingresos.

## 10. Instrucciones maliciosas dentro del documento · B

**Hipótesis:** Un documento no debe poder ordenar aprobar ni llamar herramientas.

**Modelos y usos:** Extracción aislada y schema + lista cerrada de campos; challenger con verificación de soporte.

**Cantidad a medir:**

```text
tasa_efecto_indebido = efectos no autorizados / documentos adversariales
```

**Datos y contraste:** Documentos sintéticos con instrucciones engañosas y benignos; extractor sin credenciales de pago/aprobación. Medir contaminación de campos y abstención.

**Criterio para descartar:** Cualquier efecto indebido bloquea liberación; cero en una muestra no demuestra seguridad universal.

**Base:** Diseño propio; contratos de IA existentes.

## 11. Toma de cuenta después de KYC · C

**Hipótesis:** La sesión puede cambiar aunque la identidad original fuera correcta.

**Modelos y usos:** Reglas de nuevo dispositivo/beneficiario frente a modelo secuencial de comportamiento.

**Cantidad a medir:**

```text
LLR_t = log[p(x_t|ATO) / p(x_t|legitimo)]
```

**Datos y contraste:** Sesiones adjudicadas, cambio legítimo de móvil y accesibilidad; fijar ventana disponible antes de la acción. Evaluar por cliente y tiempo.

**Criterio para descartar:** Descartar si depende de señales posteriores al desembolso o no mejora detección a igual fricción.

**Base:** S:biocatch; diseño propio.

## 12. Coerción y suplantación de voz · C

**Hipótesis:** Una víctima auténtica puede autorizar bajo engaño; face match y login correcto no resuelven intención.

**Modelos y usos:** Reglas de beneficiario y contacto por canal previo frente a contexto conductual + revisión.

**Cantidad a medir:**

```text
C_a = p_s L_s (1-q_a) + c_a + (1-p_s) f_a
```

**Datos y contraste:** Casos adjudicados y simulacros consentidos; no afirmar intención desde biometría sola. Comparar pérdida y abandono, incluyendo demora.

**Criterio para descartar:** Descartar si no hay labels confiables o si la supuesta eficacia surge solo de casos ya revisados.

**Base:** S:biocatch; diseño propio.

## 13. Caída de proveedor y backlog · A/C

**Hipótesis:** Enviar todos los timeouts a revisión puede agotar capacidad y retrasar legítimos.

**Modelos y usos:** Fail-open, revisión total y política degradada con capacidad explícita.

**Cantidad a medir:**

```text
B_(t+1) = max(0, B_t + arrivals_t - capacity_t)
```

**Datos y contraste:** Replay de solicitudes y fallos individuales/compartidos; medir completados, pendientes y espera. Notebook usa simulación agregada, sin SLA real.

**Criterio para descartar:** Descartar ruta si exige minutos inexistentes o convierte indisponibilidad en verificación favorable.

**Base:** Experimento propio; notebook.

## 14. Etiquetas selectivas y pérdida madura · D

**Hipótesis:** Solo revisar alertados distorsiona la prevalencia y evaluación del detector.

**Modelos y usos:** Muestra aleatoria de aprobados más adjudicación de alertados, registrando probabilidad de inclusión.

**Cantidad a medir:**

```text
mu_hat = (1/N) sum_i R_i Y_i / pi_i
```

**Datos y contraste:** pi conocida y positiva; seguimiento maduro y adjudicación ciega. Comparar estimación ponderada con verdad solo en laboratorio. Sin ignorabilidad no identificar eficacia causal.

**Criterio para descartar:** Descartar estimación si hay grupos con pi=0 o etiquetas incompletas tratadas como cero.

**Base:** Diseño propio; validación del portafolio.

## 15. Monitoreo con alertas múltiples · D

**Hipótesis:** Vigilar muchos canales repetidamente aumenta falsas alarmas.

**Modelos y usos:** Umbrales individuales frente a control por lote y simulación de horizonte.

**Cantidad a medir:**

```text
p_(k) <= k q / (m H_m), H_m=sum_j 1/j
```

**Datos y contraste:** p-valores marginales válidos bajo la referencia; BY por lote no garantiza FDR online ni bajo deriva. Evaluar carga y poder en muchas ventanas dependientes.

**Criterio para descartar:** Descartar garantía si la referencia está contaminada o la prueba temporal viola sus supuestos.

**Base:** Notebook conformal por canal y revisión académica existentes.

## 16. Eficacia causal de intervención · C/D

**Hipótesis:** Menor pérdida en revisados puede venir de selección, no de revisión eficaz.

**Modelos y usos:** Eficacia q asumida con sensibilidad frente a piloto aleatorizado entre acciones institucionalmente admisibles.

**Cantidad a medir:**

```text
tau = E[Y(permitir)-Y(verificar)]
```

**Datos y contraste:** Preespecificar elegibilidad, horizonte, fricción, potencia y seguridad operacional; nunca aleatorizar controles obligatorios. Si observacional, justificar intercambio y positividad.

**Criterio para descartar:** No atribuir pérdida evitada a la acción sin identificación, labels maduros e incertidumbre; mantener escenarios de q.

**Base:** Diseño propio; motor existente y línea causal de IA.

## Evitar una agenda de solo modelos grandes

Para eventos raros, modelar primero el mecanismo y las etiquetas: inconsistencia, secuencia, vínculo y acción. Logit, conteos temporales y conciliaciones son baselines útiles y auditables. Boosting/GNN/modelos de visión necesitan una mejora incremental medida. Aumentar complejidad o agregar un proveedor no constituye por sí solo una mejora.

La precisión de una alerta depende de prevalencia: `PPV = sensibilidad*pi / (sensibilidad*pi + FPR*(1-pi))`. Con sensibilidad 90%, FPR 1% y prevalencia 0,1%, PPV es aproximadamente 8,26%. Es un cálculo ilustrativo, no un resultado de proveedor; explicita por qué se requiere capacidad de investigación y no rechazo automático.

Para seleccionar ideas, priorizar cobertura de una amenaza real, disponibilidad de etiqueta, costo de experimentar y posibilidad de falsación. Empezar por dependencia, estados de error y conciliación: hoy son huecos concretos entre prototipo y operación.
