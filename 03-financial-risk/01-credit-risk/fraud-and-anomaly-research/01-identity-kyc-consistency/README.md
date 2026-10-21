# 01 · Consistencia de identidad y KYC

**S1 — diseño detallado.** Detección propuesta de suplantación, identidades sintéticas e inconsistencias entre evidencia de identidad y solicitud. No incluye un motor biométrico ni demuestra detección de deepfakes.

## Hipótesis y decisión

Hipótesis: combinar consistencia entre fuentes, historial disponible y señales del proceso de verificación permite priorizar mejor que una regla aislada. La decisión objetivo es solicitar una comprobación adicional o abrir un caso al completar KYC, antes de desembolsar. Se evalúa una fila por solicitud y versión de verificación.

Caso ilustrativo: un expediente combina discrepancias de identidad entre dos fuentes, varios reintentos y una cuenta de desembolso cuya titularidad no coincide. Cada discrepancia puede ser un error administrativo; la alerta debe mostrar qué fuentes discrepan y cómo verificarlo. El modelo no debe interpretar automáticamente una variación ortográfica como suplantación.

## Datos y variables al corte

| Familia | Variables propuestas | Control de calidad/interpretación |
|---|---|---|
| Consistencia | Coincidencia normalizada de nombre, fecha y documento entre fuentes | Normalización lingüística; diferencias de formato no son contradicciones |
| Evidencia | Vigencia, resultado de validación, confianza OCR, proveedor/versión | OCR inseguro deriva a revisión de calidad |
| Titularidad | Resultado de verificación de cuenta de desembolso | Diferenciar cuenta conjunta o desembolso autorizado |
| Dispositivo/contacto | Antigüedad conocida, solicitudes previas por ventana, cambios de contacto | No usar identificadores como categorías memorizables |
| Flujo KYC | Reintentos, fallos de fuente, duración por etapa, cobertura | Distinguir mala conectividad y accesibilidad |

La similitud de nombres no reemplaza la validación documental. Los resultados biométricos, si existen en un entorno autorizado, se incorporan como evidencia de un proveedor con controles propios; no se crean umbrales universales ni se guardan imágenes en este repositorio.

## Modelos y formulación

**Baseline 0:** reglas de incompatibilidad verificable, con razones por regla y manejo explícito de no disponible. **Baseline 1:** logit regularizado `p_i=sigmoid(beta_0+beta'x_i)` sobre etiquetas adjudicadas. La penalización y ponderación de clase se seleccionan temporalmente. El peso de clases altera probabilidades; calibrarlas en una cohorte representativa posterior.

**Challenger supervisado:** boosting tabular con interacciones entre discrepancia, cobertura y antecedentes. Comparar sin y con historial de dispositivo para medir aporte. Usar calibración sigmoidal o isotónica según tamaño de muestra, midiendo Brier y diagramas de confiabilidad.

**Challenger de novedad:** Isolation Forest entrenado sobre población histórica de referencia. Su score ordena rareza; no estima `P(fraude)`. El parámetro de contaminación no revela la prevalencia real. Mantener un canal de exploración de novedades separado de alertas probabilísticas hasta tener adjudicación suficiente.

No fusionar score biométrico, score de anomalía y probabilidad mediante suma arbitraria. Una combinación supervisada debe entrenarse con predicciones fuera de muestra y volver a calibrarse; con pocos positivos, conservar reglas y dos colas de revisión trazables.

## Etiquetas y experimentos

Confirmar tipología mediante investigación documentada; conservar sospechas sin tratarlas como positivas. Definir una ventana inicial de observación de 90 días como supuesto de trabajo y contrastar 30/60/180 días antes de fijarla con la distribución real del retraso de denuncia.

1. Generar solicitantes sintéticos legítimos con errores de digitación, nombres compuestos, conectividad deficiente y dispositivos familiares compartidos.
2. Inyectar contradicciones multifuente y reutilización coordinada, incluyendo patrones débiles y casos no detectables por las variables.
3. Comparar reglas, logit, boosting y novedad bajo iguales cortes y `K`; variar prevalencia y retraso de etiquetas.
4. Hacer ablaciones por fuente; simular caída de proveedor, cambio de OCR y nuevas campañas no vistas.
5. Medir precisión a `K`, AP, cobertura y fricción en clientes con historial corto. Publicar matriz de errores adjudicados, no solo un score global.

El simulador no puede definir fraude exactamente con las mismas reglas usadas como variables: eso haría trivial la tarea. Reservar mecanismos de generación fuera del entrenamiento y reconocer que aun así no valida fraude real.

## Refutación, entregables y aceptación

La hipótesis se debilita si el modelo solo reconoce proveedor/canal, no mejora reglas al mismo presupuesto o perjudica persistentemente a solicitantes sin historial. Un score alto por fuente caída demuestra un problema de calidad, no evidencia de ataque.

Entregables propuestos: ficha de etiquetas; generador; constructor temporal; baseline de reglas y logit; notebook de calibración/ablación; exportación de razones y cobertura. Pruebas: invariancia a futuro, estabilidad ante normalización equivalente, resultado explícito con todas las fuentes ausentes y caso legítimo con dispositivo compartido.

Pasar a S2 únicamente con ejecución reproducible y comparación sintética documentada. El paso posterior requiere datos adjudicados externos y revisión del costo de falsos positivos.

Referencia de identidad: [NIST SP 800-63A-4](https://pages.nist.gov/800-63-4/sp800-63a.html). Referencia del detector: [IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html). Son fundamentos técnicos; no se declara conformidad normativa ni desempeño.

## Integración con motores y capas

Este especialista conserva estado S1. Su familia de señal se representa mediante una variable sintética en el [motor S2 de comparación y asignación](../loss-minimization-engine/README.md); ese experimento no implementa el detector especializado descrito arriba. Véanse [capas y contratos](../ARCHITECTURE.md) y [técnicas y función de pérdida](../MODEL_AND_LOSS_METHODS.md) para el desarrollo incremental y los criterios de comparación.

## Notebooks ejecutados: experimentos S2 acotados

- [Bayes, evidencia duplicada y calibración](notebooks/01-bayes-evidence-and-calibration.ipynb)
- [Umbrales económicos y capacidad](notebooks/02-economic-thresholds-and-capacity.ipynb)

Los dos experimentos incluyen 40 celdas y cuatro figuras en conjunto. Usan datos sintéticos y no completan el detector especializado de esta ficha. Las ecuaciones y los resultados se desarrollan dentro de las celdas; las preguntas abiertas conservan estado de investigación.

[Agenda de investigación y ecuaciones adicionales](EQUATIONS_AND_RESEARCH.md) · [Reproducción y evidencia](../notebook-lab/README.md).
