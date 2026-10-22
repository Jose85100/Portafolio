# Catálogo de modelos y usos

El alcance de la revisión es la línea de fraude y anomalías: cuatro carpetas, ocho notebooks y el motor de asignación por pérdida. Cada notebook contiene directamente las fórmulas, el diccionario de símbolos/unidades y una tabla de usos. Los datos son sintéticos y los resultados no acreditan un sistema productivo.

| Familia | Qué se ajusta o resuelve | Entrada → salida | Uso concreto | Límite material |
|---|---|---|---|---|
| Bayes conjunto | Posterior analítico y dependencia por copia | Tasa base, sensibilidad, falso positivo, copia → posterior | Evaluar aporte de una segunda fuente KYC | El origen y dependencia de evidencia deben conocerse o estimarse |
| Logit | Log loss regularizada; gradiente y Hessiano conciliados | Señales de discrepancia → probabilidad | Baseline interpretable para priorizar verificación | No demuestra identidad ni causalidad |
| Calibración y prior | Sigmoide en otra ventana; odds bajo cambio de tasa base | Score congelado → probabilidad revisada | Auditar escala y pérdida económica | No corrige cualquier drift; poco positivo genera inestabilidad |
| Costo/MILP | Acción individual, capacidad y escenarios | p, pérdida, eficacia, fricción, minutos → plan | Asignar continuar, verificar o revisar | Independencia entre casos y eficacia supuesta |
| EVSI/EVPI | Enumeración de resultados de una verificación | Sensibilidad, falso positivo y costos → valor de información | Elegir si pedir evidencia antes de actuar | La prueba informativa no equivale a prevención directa |
| Red temporal | Logit individual frente a red con interacción y cobertura | Enlaces con doble fecha y evidencia → score | Medir aporte de reutilización a igual capacidad | Revisar hubs legítimos; en este test la AP no mejora |
| Cobertura de campañas | MILP y oráculo de enumeración, más escenarios | Matriz de exposición única → conjunto de acciones | Evitar doble conteo de pérdida prevenible | Cobertura y eficacia compartida no están aprendidas de datos reales |
| Ingreso cuantílico | Boosting para q0,1/q0,9 y ampliación conformal | Actividad/estación → banda de ingreso corroborado | Priorizar aclaraciones y estudiar incertidumbre | Cobertura marginal no garantiza cobertura de grupos o bajo drift |
| Ingreso de dos partes | Logit de ingreso cero + modelo lognormal positivo | Actividad → masa cero y cuantiles monetarios | Tratar ingresos realmente cero sin inventar evidencia faltante | Supuestos de distribución y categorías de evidencia |
| Conciliación/robustez | Eventos únicos, periodicidad, mediana/MAD, abstención | Flujos y referencia → ingreso/excepciones/score | Separar ingreso, traslados y financiación | No es un detector forense documental |
| Tasas de proceso | Ajuste por mezcla y contracción algebraica | Exposición/producto → residuo y tasa regularizada | Comparar grupos con poblaciones diferentes | Dependencia y política pueden explicar desvíos |
| Beta-binomial | Máxima verosimilitud en grupos de entrenamiento | Conteos → distribución predictiva y posterior de grupo | Representar sobredispersión frente a binomial | El experimento usa mezcla homogénea y no incluye incertidumbre de hiperparámetros |
| CUSUM | Umbral de una serie y máximo conjunto simulados | Residuos, dependencia, canales, horizonte → alarma | Detectar desvío persistente con carga declarada | No atribuye causa; no controla monitoreo infinito |

## Qué debe incluir una salida de modelo

Caso y población; corte de información; versión; fuente y cobertura; unidad; score y su tipo; horizonte; razones verificables; acción sugerida; costo supuesto; estado de revisión. La ausencia de evidencia es un estado del contrato y no un cero de ingreso, una validación exitosa ni una probabilidad nula.

## Cómo comparar modelos

1. Congelar población, disponibilidad de datos y horizonte de resultado.
2. Ajustar transformaciones/modelos con entrenamiento y calibración posterior cuando corresponda.
3. Evaluar discriminación, escala, falsos positivos y cobertura por grupo.
4. Comparar acción/costo con el mismo menú y capacidad; no atribuir al modelo una mejora obtenida por cambiar acciones.
5. Conservar fallos: red sin mejora, calibración peor o cobertura perdida bajo drift son resultados útiles.
6. Reservar una cohorte externa para elegir una versión institucional y estimar la eficacia de las acciones.

[Índice de notebooks](notebook-lab/README.md) · [Arquitectura](ARCHITECTURE.md) · [Técnicas y pérdida](MODEL_AND_LOSS_METHODS.md).
