# 1. Auditoría de confusión temporal: predicción no identifica intervención

CICLO_DIARIO25oct2026, dominio02, programa06. Base revisada: main98659cc; PRabiertos ninguno al consultar. No repite firmas de23/24.

## 2. Tres ideas, elección e hipótesis

| Idea | Ventaja | Motivo de elección/descarte |
|---|---|---|
| Persistencia H0/MST bajo cambios de escala, programa07 | Invariantes geométricos ejecutables | Requiere fijar umbrales de interpretación; pospuesta |
| Consistencia de medidas por ciclos, programa17 | Certificados lineales y límites observables | Solapa parcialmente la auditoría gauge12; pospuesta |
| Confusión temporal conocida, programa06 | Contrasta estimando estadístico y efecto SCM con verdad analítica | Elegida: brecha explícita entre predicción e intervención |

Hipótesis preregistrada en config.json: con control correcto, rechazo bajo β=0<=10% por tamaño, potencia>=80% para β=.3 y n>=500, sesgo medio absoluto<.03 en n2000. No se exige eliminar la asociación predictiva omitida: realmente existe. Novedad incremental local: transformar diseño S1 en banco de falsación con alineamiento, oráculos e intervención emparejada, no inventar OLS, F-test o causal discovery.

## 3. Estado del arte
Granger operacionaliza precedencia predictiva; Pearl y Petersetal distinguen asociación, estructura e intervención; Rungeetal estudian causal discovery con independencia condicional en sistemas generales; Shojaie–Fox revisan avances y límites. Cinco referencias reales verificadas en fuentes.md y referencias.bib. Este MVP no implementa PCMCI ni compara rendimiento con esos sistemas; no se reclama prioridad mundial o revisión exhaustiva.

## 4. Brecha
El programa06 solo formulaba preguntas sobre feedback y confusión. No había generador ni test que pudiera refutar una lectura causal de asociaciones temporales. Se cierra una esquina lineal/gaussiana sin feedback; el programa general permanece incompleto.

## 5. Diseño experimental y config
Z_t iidN(0,1), innovaciones independientes ux_t,uy_t iidN(0,.25). X_t=.8Z_(t−1)+ux_t; Y_t=βX_(t−1)+.8Z_(t−2)+uy_t. Se generan n+2 valores y se alinean t=2,...,n+1. El núcleo(Xlag,Zlag2,Y) tiene filas independientes: no se disfraza un VAR autocorrelacionado como regresión IID.

n100/500/2000, β0/.3,200 réplicas independientes por configuración, seed20261025 más desplazamiento determinista registrado en cada fila. Son1200 datasets, cuatro métodos pareados por dataset,4800 ajustes. Comparadores: sin control, Zlag2 verdadero, Z en lag incorrecto y proxyW=Zlag2+v con v~N(0,1). Parámetros del DGP fijados en config y contrastados por assert; no se cambian silenciosamente. No hay selección de lags ni tuning sobre resultados.

## 6. Implementación y derivaciones
OLS anidado restringido sobre intercepto+controles y ampliado añadiendo Xlag. F=(RSS_R−RSS_U)/(RSS_U/(n−p)); p_val=Pr(F_(1,n−p)>=F). CI95% del coeficiente usa t_(n−p). Lstsq/pseudoinversa evitan invertir directamente ecuaciones normales; se rechaza rango deficiente y varianza residual nula. La referencia exacta requiere errores gaussianos IID independientes del diseño completo; vale para el control correcto. La ablación con lag erróneo expone Z de filas adyacentes y no tiene garantía exacta de F condicional: sus p-valores son diagnósticos sin calibración alegada.

Sesgo del estimando omitido frente a β: Cov(Xlag,.8Zlag2)/Var(Xlag)=.64/(.64+.25)=.719101. Por tanto la pendiente omitida converge a β+.719101: es una asociación poblacional real. Con proxy ruidoso de varianza1, Cov(X,Z|W)=.8−.8/2=.4 y Var(X|W)=.89−.64/2=.57; exceso de pendiente=.8*.4/.57=.561404. Con Z verdadero residualizar X deja ux y residualizar Y deja βux+uy, recuperando β.

La intervención emparejada do(Xlag←Xlag+δ) conserva exógenos y da ΔY=βδ. Es identidad del SCM conocido, no validación independiente de causalidad en datos reales.

## 7. Tests y benchmarks ejecutados
Seis tests pasan: reproducibilidad/alineamiento/intervención, oracle independiente scipy.linregress, invariancia afín y FWL, diez casos aleatorios FWL/F=t², recuperación de límites n10000, entradas/rango/varianza degeneradas. Ruff y mypy src pasan. Cobertura medida100% de74 sentencias de src.confounding; no significa cobertura de todas las ramas, notebook o repo. Benchmark guarda tiempo por ajuste y pico de asignaciones Python tracemalloc, no RSS, sobre tres tamaños. No hay C/C++ nuevo; sanitizers no aplican. La precisión es sesgo/coverage, estabilidad incluye invariancia de unidades y errores de medida del control, escalabilidad está en summary.csv; no se afirma velocidad universal.

## 8. Resultados con incertidumbre

A n500,200 réplicas por celda:

| β | Método | Rechazo de asociación | Pendiente media | Coverage CI frente a β |
|---|---|---:|---:|---:|
| 0 | Omitido |100%|.721238|0%|
| 0 | Control correcto |4.5%|−.006267|95.5%|
| 0 | Lag incorrecto |100%|.721112|0%|
| 0 | Proxy ruidoso |100%|.556913|0%|
| .3 | Omitido |100%|1.020851|0%|
| .3 | Control correcto |100%|.300080|96%|
| .3 | Lag incorrecto |100%|1.020846|0%|
| .3 | Proxy ruidoso |100%|.860964|0%|

El4.5% tiene intervalo binomial MC95%Clopper–Pearson[2.078%,8.370%]. Para200/200, límite inferior98.172%. Son intervalos sobre repetición del procedimiento, no del efecto. Los métodos comparten datasets y no deben tratarse como réplicas independientes al comparar métodos. La coverage frente a β para omitido no es falta de coverage de su propio parámetro de asociación: indica estimando equivocado para pregunta causal. Todos los umbrales registrados pasan. Resultados crudos en results/replicates.csv, resumen completo en summary.csv/summary.json, figura audit.png.

## 9. Análisis crítico y ablaciones negativas
Añadir datos no corrige confusor omitido: concentra alrededor del parámetro equivocado para la pregunta causal. Añadir un control no basta: lag erróneo y proxy ruidoso mantienen el sesgo. El contraste omitido no falla al rechazar ausencia de asociación; la asociación existe incluso con β0. El caso controlado es favorable por diseño y no demuestra selección correcta de controles en problemas desconocidos. No se promueve significancia a intervención y no se transforma una identidad implementada del SCM en prueba empírica.

## 10. Límites, sesgos, madurez
Linealidad, Gaussianidad, ausencia de feedback y verdad de lag/control dadas al analista. No se resuelven confusores ocultos, causal discovery no lineal, autocorrelación general o muestreo irregular. El p-valor no cuantifica probabilidad de causalidad. La ablación de lag erróneo no ofrece calibración exacta. No hay datos reales, privacidad de clientes ni afirmaciones regulatorias. ComponenteS2 limitado, no todo el programa ni dominio. EL83 no aplica. Notebook ejecutado realmente con IPython in-process y namespace nuevo; kernel Jupyter separado no probado.

## 11. Comando reproducible
Desde esta carpeta, Python3.12: `bash run.sh`. Bootstrap crea .venv con pins e instala todas las dependencias; MATH_ENV selecciona entorno alternativo. Seis tests, lint, tipos, cobertura,4800 ajustes, notebook y figura se regeneran sin datos externos. Recursos y versiones quedan registrados.

## 12. Referencias BibTeX
Cinco entradas completas en referencias.bib con DOI/URL; fuentes.md distingue accesos primarios válidos, bloqueos y alcance de lectura. La bibliografía contextualiza; no sustituye resultados ejecutados ni se afirma haber implementado todos sus algoritmos.

## 13. Autoevaluación1–5
Novedad2 (falsación local, métodos clásicos); rigor4 (oráculo, derivaciones, límites exactos del F); reproducibilidad4 (pins, seeds, resultados y notebook ejecutado); código4; claridad4; impacto3 (enseñanza y validación sintética); honestidad5; MVP ejecutable5. No certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: introducir autocorrelación y evaluar inferencia robusta sin mantener indebidamente la referencia F exacta.

1. `advanced-research/06-nonlinear-dynamic-causal-discovery`: añadir errores AR y comparar HAC/bootstrap temporal con nulidad correctamente definida.
2. `advanced-research/06-nonlinear-dynamic-causal-discovery`: contrastar PCMCI bajo mismas seeds y supuestos antes de afirmar comparación avanzada.
3. `advanced-research/06-nonlinear-dynamic-causal-discovery`: estudiar medición ruidosa con varianza conocida, mostrando qué información extra permite identificación.
